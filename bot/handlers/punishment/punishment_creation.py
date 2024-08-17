import re
from datetime import timedelta, datetime
from uuid import uuid4

from aiogram import Router, F
from aiogram.enums import ChatType, ContentType
from aiogram.filters import Command, MagicData
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery
from aiogram.utils.formatting import Text, BlockQuote
from django.conf import settings
from django.utils.translation import gettext as _
from sympy.physics.units import second

from bot.generate_session import bot
from bot.models import ChatMember
from games.models import Punishment
from .PunishmentCreationStates import PunishmentCreationStates
from ...filters import DialogAccessFilter
from ...filters.ReplyToCorrectMessageFilter import ReplayToCorrectMessageFilter

from .keyboards import get_punishment_privacy_selection_keyboard
from shared import redis

punishment_creation_router = Router()
punishment_creation_router.message.filter(MagicData(F.chat.type.is_not(ChatType.PRIVATE)), F.from_user.id.in_(settings.ADMINS))
punishment_creation_router.callback_query.filter(F.data.startswith("pc"), DialogAccessFilter())


@punishment_creation_router.message(Command(settings.CREATE_PUNISHMENT_COMMAND))
async def create_punishment_command(message: Message, state: FSMContext):
    await state.clear()
    await state.set_state(PunishmentCreationStates.choosing_name)
    data = await state.get_data()

    # Translators: choosing name for new punishment
    bot_message = await message.answer(text=_("To create a punishment, you need to write the name of the new punishment in response to this "
                                              "message."))
    data["message_id"] = bot_message.message_id
    await state.set_data(data)

    await message.delete()


@punishment_creation_router.message(PunishmentCreationStates.choosing_name,
                                    F.content_type == ContentType.TEXT,
                                    ReplayToCorrectMessageFilter("message_id"))
async def choose_name(message: Message, state: FSMContext):
    await state.set_state(PunishmentCreationStates.choosing_time)
    data = await state.get_data()

    data["name"] = message.text

    # Translators: choosing time for new punishment
    await bot.delete_message(chat_id=message.chat.id, message_id=data["message_id"])
    new_message = await message.answer(**Text(_("Name: %(name)s\n\n"
                                  "Now in response to this message write the time of punishment" % {"name": message.text}),
                                _("Time can be specified in any of the following ways:"),
                                BlockQuote(_("5:30 – 5 hours and 30 minutes\n"
                                             "30 – 30 minutes\n"
                                             "5 30 – the same as first\n"
                                             "1:0:0 – 1 day\n"
                                             "1 5 0 – 1 day and 5 hours\n"
                                             "40:00 – 40 hours\n"
                                             "100 – 100 minutes\n"))
                                ).as_kwargs()
                         )

    data["message_id"] = new_message.message_id
    await state.set_data(data)

    await message.delete()


@punishment_creation_router.message(PunishmentCreationStates.choosing_time,
                                    F.text.regexp(r"\d+"),
                                    F.content_type == ContentType.TEXT,
                                    ReplayToCorrectMessageFilter("message_id"))
async def choose_name(message: Message, member: ChatMember, state: FSMContext):
    data = await state.get_data()
    await state.clear()

    matches = re.findall(r"\d+", message.text)
    days, hours, minutes = (0,) * (3 - len(matches)) + tuple(map(int, matches))
    time = timedelta(days=days, hours=hours, minutes=minutes)

    new_data = await redis.get_or_set(str(member.id))
    if "dialogs" not in new_data:
        new_data["dialogs"] = {}
    dialog_id = str(uuid4())
    new_data["dialogs"][dialog_id] = {"date": str(datetime.utcnow()), "name": data["name"], "time": time.total_seconds()}
    await redis.set_serialized(str(member.id), new_data)

    await bot.delete_message(chat_id=member.chat_id, message_id=int(data["message_id"]))
    # Translators: privacy selection message
    await message.answer(text=_("Now select the privacy of the new punishment"),
                         reply_markup=get_punishment_privacy_selection_keyboard(dialog_id))
    await message.delete()


@punishment_creation_router.callback_query()
async def choose_privacy(callback: CallbackQuery, member: ChatMember):
    callback_data = callback.data.split(':')[1:]
    dialog_id = callback_data[1]
    is_public = bool(int(callback_data[0]))

    data = await redis.get_deserialized(str(member.id))
    data["dialogs"].pop(dialog_id)
    await redis.set_serialized(str(member.id), data)

    punishment = Punishment(name=data["dialogs"][dialog_id]["name"],
                            time=timedelta(seconds=int(data["dialogs"][dialog_id]["time"])),
                            created_by=member,
                            is_public=is_public)
    await punishment.asave()


    await callback.message.answer(text=_("Punishment '%(punishment)s' successfully created" % {"punishment": punishment.get_string()}))
    await callback.message.delete()

