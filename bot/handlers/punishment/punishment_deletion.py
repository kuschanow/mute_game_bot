from typing import Dict, Any

from aiogram import Router, F
from aiogram.enums import ChatType
from aiogram.filters import MagicData, Command
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery
from aiogram.types import Message
from aiogram_dialog_manager import DialogInstance, DialogManager
from aiogram_dialog_manager.filter import ButtonFilter, DialogFilter
from aiogram_dialog_manager.filter.access import DialogAccessFilter
from asgiref.sync import sync_to_async
from django.conf import settings
from django.utils.translation import gettext as _

from bot.utils.punishment_selection_keyboard import get_punishments_keyboard
from bot.models import ChatMember, AccessSettingsObject, User
from games.models import Punishment
from shared import category

punishment_deletion_router = Router()
punishment_deletion_router.message.filter(MagicData(F.chat.type.is_not(ChatType.PRIVATE)))
punishment_deletion_router.callback_query.filter(DialogAccessFilter(), DialogFilter("punishment_deletion"))


@punishment_deletion_router.message(Command(settings.DELETE_PUNISHMENT_COMMAND))
async def delete_punishments_command(message: Message, state: FSMContext, user: User, dialog_manager: DialogManager, member, member_settings: AccessSettingsObject):
    await state.clear()
    dialog: DialogInstance = dialog_manager.create_dialog(prototype_name="punishment_deletion", user_id=user.id, chat_id=message.chat.id)
    dialog.values["prefix"] = _("Dialog with ") + user.get_string(True) + "\n\n"
    public_indicator = 1 if member_settings.can_delete_public_punishments else 0
    dialog.values["public_indicator"] = public_indicator
    dialog.values["category"] = category[public_indicator]
    dialog.values["page"] = 0
    bot_message = await dialog.send_message("select", await get_punishments_keyboard(member, member_settings, public_indicator, dialog.values["page"]))
    dialog.values["main_message_id"] = bot_message.message_id
    await dialog_manager.save_dialog(dialog)
    await message.delete()


@punishment_deletion_router.callback_query(ButtonFilter("privacy"))
async def select_punishments_privacy(callback: CallbackQuery, dialog: DialogInstance, button_data: Dict[str, Any], member, member_settings):
    await callback.answer()
    keyboard = await get_punishments_keyboard(member, member_settings, button_data["public_indicator"], 0)
    dialog.values["public_indicator"] = button_data["public_indicator"]
    dialog.values["category"] = category[button_data["public_indicator"]]
    dialog.values["page"] = 0
    await dialog.edit_message(callback.message.message_id, "select", keyboard)


@punishment_deletion_router.callback_query(ButtonFilter("change_page"))
async def select_page(callback: CallbackQuery, dialog: DialogInstance, button_data: Dict[str, Any], member, member_settings):
    await callback.answer()
    keyboard = await get_punishments_keyboard(member, member_settings, dialog.values["public_indicator"], button_data["page"])
    dialog.values["page"] = button_data["page"]
    await dialog.edit_message(callback.message.message_id, "select", keyboard)


@punishment_deletion_router.callback_query(ButtonFilter("punishment"))
async def select_punishment(callback: CallbackQuery, dialog: DialogInstance, button_data: Dict[str, Any], user: User):
    await callback.answer()
    dialog.values["punishment_name"] = button_data["name"]
    await dialog.send_message("accept", [[("accept", {"id": button_data["id"]})], ["refuse"]])


@punishment_deletion_router.callback_query(ButtonFilter("accept"))
async def accept(callback: CallbackQuery, member: ChatMember, dialog: DialogInstance, button_data: Dict[str, Any], member_settings: AccessSettingsObject):
    punishment_id = button_data["id"]

    punishment = await Punishment.objects.aget(id=punishment_id)

    if await sync_to_async(lambda: punishment.randomchoicegame_set.count() > 0)():
        punishment.is_deleted = True
        await punishment.asave()
    else:
        await punishment.adelete()

    await callback.answer(_("Deleted"))
    await dialog.delete_message(callback.message.message_id)

    try:
        keyboard = await get_punishments_keyboard(member, member_settings, dialog.values["public_indicator"], dialog.values["page"])
    except:
        dialog.values["page"] = dialog.values["page"] - 1
        keyboard = await get_punishments_keyboard(member, member_settings, dialog.values["public_indicator"], dialog.values["page"])

    await dialog.edit_keyboard(dialog.values["main_message_id"], keyboard)


@punishment_deletion_router.callback_query(ButtonFilter("refuse"))
async def refuse_deletion(callback: CallbackQuery, dialog: DialogInstance):
    await callback.answer(_("Ok"))
    await dialog.delete_message(callback.message.message_id)


@punishment_deletion_router.callback_query(ButtonFilter("cancel"))
async def cancel(callback: CallbackQuery, dialog: DialogInstance, dialog_manager: DialogManager):
    await callback.answer(_("Ok"))
    await dialog.delete_all_messages()
    await dialog_manager.delete_dialog(dialog)
