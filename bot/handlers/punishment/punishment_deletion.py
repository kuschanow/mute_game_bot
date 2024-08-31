from datetime import datetime

from aiogram import Router, F
from aiogram.enums import ChatType
from aiogram.filters import MagicData, Command
from aiogram.types import CallbackQuery
from aiogram.types import Message
from asgiref.sync import sync_to_async
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
    data = await redis.get_deserialized(str(member.id))
    if "dialogs" not in data:
        data["dialogs"] = {}
    public_indicator = 1 if member_settings.can_delete_public_punishments else 0
    keyboard = await get_punishments_keyboard(member, member_settings, public_indicator, 0)

    dialog_message = await message.answer(text=_("Choose a punishment from the list below\n\n"
                                              "Category: %(category)s" % {"category": _("Public")}), reply_markup=keyboard)

    data["dialogs"][str(dialog_message.message_id)] = {"datetime": str(datetime.utcnow()), "public_indicator": public_indicator, "page": 1}
    await redis.set_serialized(str(member.id), data)

    await message.delete()


@punishment_deletion_router.callback_query(F.data.contains("p_category"))
async def select_punishments_category(callback: CallbackQuery, member: ChatMember, member_settings: AccessSettingsObject):
    callback_data = callback.data.split(':')[2:]
    page = int(callback_data[1])
    public_indicator = int(callback_data[0])
    keyboard = await get_punishments_keyboard(member, member_settings, public_indicator, page)
    dialog_id = str(callback.message.message_id)

    data = await redis.get_deserialized(str(member.id))
    dialog = data["dialogs"][dialog_id]
    dialog["public_indicator"] = public_indicator
    dialog["page"] = page
    data["dialogs"][dialog_id] = dialog
    await redis.set_serialized(str(member.id), data)

    await callback.message.edit_text(text=_("Choose a punishment from the list below\n\n"
                                            "Category: %(category)s" % {"category": category[public_indicator]}),
                                     reply_markup=keyboard)


@punishment_deletion_router.callback_query(F.data.contains("p_select"))
async def choose_privacy(callback: CallbackQuery, member: ChatMember):
    callback_data = callback.data.split(':')[2:]
    punishment_id = callback_data[0]

    dialog_id = str(callback.message.message_id)

    data = await redis.get_deserialized(str(member.id))
    dialog = data["dialogs"][dialog_id]

    # Translators: deletion acceptance dialogue
    deletion_message = await callback.message.reply(text=_("Accept deletion for %(punishment)s" % {"punishment": (await Punishment.objects.aget(id=punishment_id)).get_string()}),
                                     reply_markup=get_acceptance_keyboard(punishment_id))

    if "deletion_message_id" in dialog:
        try:
            await bot.delete_message(chat_id=callback.message.chat.id, message_id=dialog["deletion_message_id"])
        except:
            pass
    dialog["deletion_message_id"] = deletion_message.message_id
    data["dialogs"][dialog_id] = dialog
    data["dialogs"][deletion_message.message_id] = {"datetime": str(datetime.utcnow())}
    await redis.set_serialized(str(member.id), data)
    await callback.answer()


@punishment_deletion_router.callback_query(F.data.contains("accept"))
async def accept(callback: CallbackQuery, member: ChatMember, member_settings: AccessSettingsObject):
    callback_data = callback.data.split(':')[2:]
    punishment_id = callback_data[0]

    dialog_id = str(callback.message.reply_to_message.message_id)

    data = await redis.get_deserialized(str(member.id))
    dialog = data["dialogs"][dialog_id]

    punishment = await Punishment.objects.aget(id=punishment_id)

    if await sync_to_async(lambda: punishment.randomchoicegame_set.count() > 0)():
        punishment.is_deleted = True
        await punishment.asave()
    else:
        await punishment.adelete()

    dialog.pop("deletion_message_id")

    await callback.answer(_("Deleted"))
    await callback.message.delete()

    try:
        keyboard = await get_punishments_keyboard(member, member_settings, int(dialog["public_indicator"]), int(dialog["page"]))
    except:
        keyboard = await get_punishments_keyboard(member, member_settings, int(dialog["public_indicator"]), int(dialog["page"]) - 1)
        dialog["page"] = int(dialog["page"]) - 1

    await bot.edit_message_text(chat_id=member.chat_id, message_id=callback.message.reply_to_message.message_id,
                                text=_("Choose a punishment from the list below\n\n"
                                       "Category: %(category)s" % {"category": category[int(dialog["public_indicator"])]}),
                                reply_markup=keyboard)

    data["dialogs"][dialog_id] = dialog
    data["dialogs"].pop(str(callback.message.message_id))
    await redis.set_serialized(str(member.id), data)


@punishment_deletion_router.callback_query(F.data.contains("refuse"))
async def cancel_deletion(callback: CallbackQuery, member: ChatMember):
    dialog_id = str(callback.message.reply_to_message.message_id)

    data = await redis.get_deserialized(str(member.id))
    dialog = data["dialogs"][dialog_id]
    dialog.pop("deletion_message_id")
    data["dialogs"][dialog_id] = dialog
    data["dialogs"].pop(str(callback.message.message_id))
    await redis.set_serialized(str(member.id), data)

    await callback.answer(_("Ok"))
    await callback.message.delete()


@punishment_deletion_router.callback_query(F.data.contains("cancel"))
async def cancel(callback: CallbackQuery, member: ChatMember):
    user_data = await redis.get_deserialized(str(member.id))
    user_data["dialogs"].pop(str(callback.message.message_id))

    await redis.set_serialized(str(member.id), user_data)

    await callback.answer(_("Ok"))
    await callback.message.delete()
