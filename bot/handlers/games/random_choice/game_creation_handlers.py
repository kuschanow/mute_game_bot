from datetime import datetime

from aiogram import Router, F
from aiogram.enums import ChatType
from aiogram.filters import Command, MagicData
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery
from asgiref.sync import sync_to_async
from django.conf import settings
from django.utils.translation import gettext as _

from bot.filters import DialogAccess
from bot.models import ChatMember, User
from bot.models.AccessSettingsObject import AccessSettingsObject
from games.models import RandomChoiceGame
from shared import redis, category
from .utils.keyboards import get_punishments_keyboard, get_game_settings_keyboard

game_creation_router = Router()
game_creation_router.message.filter(MagicData(F.chat.type.is_not(ChatType.PRIVATE)))
game_creation_router.callback_query.filter(F.data.startswith("rcgc"), DialogAccess())


@game_creation_router.message(Command(settings.RANDOM_CHOICE_GAME_COMMAND))
async def start_game_command(message: Message, member: ChatMember, user: User, member_settings: AccessSettingsObject, state: FSMContext):
    if not member_settings.can_create_games:
        await message.answer(_("You cannot create games"))
        await message.delete()
        return

    await state.clear()

    data = await redis.get_deserialized(str(member.id))
    if "dialogs" not in data:
        data["dialogs"] = {}

    keyboard = await get_punishments_keyboard(member, member_settings, 1, 0)

    dialog_message = await message.answer(text=user.get_string(True) +
                                               "\n\n" +
                                               _("Choose a punishment from the list below\n\n"
                                                 "Category: %(category)s" % {"category": _("Public")}),
                         reply_markup=keyboard)
    await message.delete()

    data["dialogs"][dialog_message.message_id] = {"datetime": str(datetime.utcnow())}
    await redis.set_serialized(str(member.id), data)


@game_creation_router.callback_query(F.data.contains("p_category"))
async def select_punishments_category(callback: CallbackQuery, member: ChatMember, member_settings: AccessSettingsObject):
    callback_data = callback.data.split(':')[2:]
    page = int(callback_data[1])
    public_indicator = int(callback_data[0])
    keyboard = await get_punishments_keyboard(member, member_settings, public_indicator, page)
    await callback.message.edit_text(text=_("Choose a punishment from the list below\n\n"
                                            "Category: %(category)s" % {"category": category[public_indicator]}),
                                     reply_markup=keyboard)

@game_creation_router.callback_query(F.data.contains("p_select"))
async def select_punishment(callback: CallbackQuery, member: ChatMember, member_settings: AccessSettingsObject):
    callback_data = callback.data.split(':')[2:]
    punishment_id = callback_data[0]

    game = RandomChoiceGame(punishment_id=punishment_id,
                            creator=member)
    await sync_to_async(lambda: game.clean())()
    await game.asave()

    data = await redis.get_deserialized(str(member.id))
    data["dialogs"][callback.message.message_id] = {"datetime": str(datetime.utcnow())}
    await redis.set_serialized(str(member.id), data)

    await callback.message.edit_text(text=await game.get_string(), reply_markup=get_game_settings_keyboard(game, member_settings))


@game_creation_router.callback_query(F.data.contains("cancel"))
async def cancel(callback: CallbackQuery, member: ChatMember):
    user_data = await redis.get_deserialized(str(member.id))
    user_data["dialogs"].pop(str(callback.message.message_id))

    await redis.set_serialized(str(member.id), user_data)

    await callback.answer(_("Ok"))
    await callback.message.delete()

