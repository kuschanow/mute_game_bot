from datetime import datetime
from typing import Dict
from uuid import uuid4

from aiogram import Router, F
from aiogram.enums import ChatType
from aiogram.filters import MagicData, Command
from aiogram.types import CallbackQuery
from aiogram.types import Message
from django.conf import settings
from django.utils.translation import gettext as _

from bot.filters import DialogAccess
from bot.generate_session import bot
from bot.handlers.punishment.utils.keyboards import get_punishments_keyboard, get_acceptance_keyboard
from bot.models import ChatMember, AccessSettingsObject
from games.models import Punishment
from shared import redis, category

punishment_deletion_router = Router()
punishment_deletion_router.message.filter(MagicData(F.chat.type.is_not(ChatType.PRIVATE)))
punishment_deletion_router.callback_query.filter(F.data.startswith("pd"), DialogAccess())


@punishment_deletion_router.message(Command(settings.DELETE_PUNISHMENT_COMMAND))
async def delete_punishments_command(message: Message, member: ChatMember, member_settings: AccessSettingsObject):
    new_data = await redis.get_or_set(str(member.id))
    if "dialogs" not in new_data:
        new_data["dialogs"] = {}
    dialog_id = str(uuid4())
    category = 1 if member_settings.can_delete_public_punishments else 0
    keyboard, punishments_mapping = await get_punishments_keyboard(dialog_id, member, member_settings, category, 1)

    dialog_message = await message.answer(text=_("Choose a punishment from the list below\n\n"
                                              "Category: %(category)s" % {"category": _("Public")}), reply_markup=keyboard)

    new_data["dialogs"][dialog_id] = {"date": str(datetime.utcnow()), "mapping": punishments_mapping, "dialog_message_id": dialog_message.message_id, "category": category, "page": 1}
    await redis.set_serialized(str(member.id), new_data)

    await message.delete()


@punishment_deletion_router.callback_query(F.data.contains("p_category"))
async def select_punishments_category(callback: CallbackQuery, member: ChatMember, member_settings: AccessSettingsObject):
    callback_data = callback.data.split(':')[2:]
    dialog_id = callback_data[2]
    page = int(callback_data[1])
    public_indicator = int(callback_data[0])
    keyboard, punishments_mapping = await get_punishments_keyboard(dialog_id, member, member_settings, public_indicator, page)

    data = await redis.get_deserialized(str(member.id))
    dialog = data["dialogs"][dialog_id]
    dialog["mapping"] = punishments_mapping
    dialog["category"] = public_indicator
    dialog["page"] = page
    data["dialogs"][dialog_id] = dialog
    await redis.set_serialized(str(member.id), data)

    await callback.message.edit_text(text=_("Choose a punishment from the list below\n\n"
                                            "Category: %(category)s" % {"category": category[public_indicator]}),
                                     reply_markup=keyboard)


@punishment_deletion_router.callback_query(F.data.contains("p_select"))
async def choose_privacy(callback: CallbackQuery, member: ChatMember):
    callback_data = callback.data.split(':')[2:]
    dialog_id = callback_data[1]
    punish_num = callback_data[0]

    data = await redis.get_deserialized(str(member.id))
    dialog = data["dialogs"][dialog_id]
    dialog["delete_this"] = dialog["mapping"][punish_num]

    # Translators: deletion acceptance dialogue
    deletion_message = await callback.message.answer(text=_("Accept deletion for %(punishment)s" % {"punishment": (await Punishment.objects.aget(id=dialog["delete_this"])).get_string()}),
                                     reply_markup=get_acceptance_keyboard(dialog_id))

    if "deletion_message_id" in dialog:
        await bot.delete_message(chat_id=callback.message.chat.id, message_id=dialog["deletion_message_id"])
    dialog["deletion_message_id"] = deletion_message.message_id
    data["dialogs"][dialog_id] = dialog
    await redis.set_serialized(str(member.id), data)
    await callback.answer()


@punishment_deletion_router.callback_query(F.data.contains("accept"))
async def accept(callback: CallbackQuery, member: ChatMember, member_settings: AccessSettingsObject):
    callback_data = callback.data.split(':')[2:]
    dialog_id = callback_data[0]

    data = await redis.get_deserialized(str(member.id))
    dialog = data["dialogs"][dialog_id]

    await (await Punishment.objects.aget(id=dialog["delete_this"])).adelete()

    dialog.pop("deletion_message_id")
    dialog.pop("delete_this")

    await callback.answer(_("Deleted"))
    await callback.message.delete()

    try:
        keyboard, punishments_mapping = await get_punishments_keyboard(dialog_id, member, member_settings, int(dialog["category"]), int(dialog["page"]))
    except:
        keyboard, punishments_mapping = await get_punishments_keyboard(dialog_id, member, member_settings, int(dialog["category"]), int(dialog["page"]) - 1)
        dialog["page"] = int(dialog["page"]) - 1

    dialog["mapping"] = punishments_mapping

    await bot.edit_message_text(chat_id=member.chat_id, message_id=int(dialog["dialog_message_id"]),
                                text=_("Choose a punishment from the list below\n\n"
                                       "Category: %(category)s" % {"category": category[int(dialog["category"])]}),
                                reply_markup=keyboard)

    data["dialogs"][dialog_id] = dialog
    await redis.set_serialized(str(member.id), data)


@punishment_deletion_router.callback_query(F.data.contains("refuse"))
async def cancel_deletion(callback: CallbackQuery, member: ChatMember):
    callback_data = callback.data.split(':')[2:]
    dialog_id = callback_data[0]

    data = await redis.get_deserialized(str(member.id))
    dialog = data["dialogs"][dialog_id]
    dialog.pop("deletion_message_id")
    dialog.pop("delete_this")
    data["dialogs"][dialog_id] = dialog
    await redis.set_serialized(str(member.id), data)

    await callback.answer(_("Ok"))
    await callback.message.delete()


@punishment_deletion_router.callback_query(F.data.contains("cancel"))
async def cancel(callback: CallbackQuery, member: ChatMember):
    dialog_id = callback.data.split(':')[-1]

    user_data = await redis.get_deserialized(str(member.id))
    user_data["dialogs"].pop(dialog_id)

    await redis.set_serialized(str(member.id), user_data)

    await callback.answer(_("Ok"))
    await callback.message.delete()
