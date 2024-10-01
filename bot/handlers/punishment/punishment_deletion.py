from typing import Dict, Any

from aiogram import Router, F
from aiogram.enums import ChatType
from aiogram.filters import MagicData, Command
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery
from aiogram.types import Message
from aiogram_dialog_manager import Dialog
from aiogram_dialog_manager import DialogManager
from aiogram_dialog_manager.filter import ButtonFilter, DialogFilter
from aiogram_dialog_manager.filter.access import DialogAccessFilter
from aiogram_dialog_manager.instance import ButtonInstance
from asgiref.sync import sync_to_async
from django.conf import settings
from django.utils.translation import gettext as _

from bot.generate_session import bot
from bot.models import ChatMember, AccessSettingsObject, User
from bot.utils.dialog.dialog_buttons import privacy, change_page, punishment, accept, refuse
from bot.utils.dialog.dialog_menus import punishments, accept as accept_menu
from bot.utils.dialog.dialog_texts import punishment_deletion_texts
from games.models import Punishment
from shared import category

punishment_deletion_router = Router()
punishment_deletion_router.message.filter(MagicData(F.chat.type.is_not(ChatType.PRIVATE)))
punishment_deletion_router.callback_query.filter(DialogAccessFilter(), DialogFilter("punishment_deletion"))


@punishment_deletion_router.message(Command(settings.DELETE_PUNISHMENT_COMMAND))
async def delete_punishments_command(message: Message, state: FSMContext, user: User, dialog_manager: DialogManager, member: ChatMember):
    await state.clear()

    dialog: Dialog = Dialog.create("punishment_deletion", user_id=user.id, chat_id=message.chat.id, bot=bot)
    dialog.data["prefix"] = _("Dialog with ") + user.get_string(True) + "\n\n"
    public_indicator = 1 if member.access_settings.can_delete_public_punishments else 0
    dialog.data["public_indicator"] = public_indicator
    dialog.data["category"] = category[public_indicator]
    dialog.data["page"] = 0

    bot_message = await dialog.send_message(punishment_deletion_texts["select"], punishments, menu_data={"chat_member": member})
    dialog.data["main_message_id"] = bot_message.message_id
    await dialog_manager.save_dialog(dialog)
    await message.delete()


@punishment_deletion_router.callback_query(ButtonFilter(privacy))
async def select_punishments_privacy(callback: CallbackQuery, dialog: Dialog, button: ButtonInstance, member: ChatMember):
    await callback.answer()
    dialog.data["public_indicator"] = button.data["public_indicator"]
    dialog.data["category"] = category[button.data["public_indicator"]]
    dialog.data["page"] = 0

    await dialog.edit_message(callback.message.message_id, punishment_deletion_texts["select"], punishments, menu_data={"chat_member": member})


@punishment_deletion_router.callback_query(ButtonFilter(change_page))
async def select_page(callback: CallbackQuery, dialog: Dialog, button_data: Dict[str, Any], member: ChatMember):
    await callback.answer()
    dialog.data["page"] = button_data["page"]

    await dialog.edit_message(callback.message.message_id, punishment_deletion_texts["select"], punishments, menu_data={"chat_member": member})


@punishment_deletion_router.callback_query(ButtonFilter(punishment))
async def select_punishment(callback: CallbackQuery, dialog: Dialog, button: ButtonInstance):
    await callback.answer()
    dialog.data["punishment_name"] = button.data["name"]
    await dialog.send_message(punishment_deletion_texts["accept"], accept_menu, menu_data={"p_id": button.data["id"]})


@punishment_deletion_router.callback_query(ButtonFilter(accept))
async def accept(callback: CallbackQuery, member: ChatMember, dialog: Dialog, button: ButtonInstance):
    punishment_id = button.data["id"]

    punishment = await Punishment.objects.aget(id=punishment_id)

    if await sync_to_async(lambda: punishment.randomchoicegame_set.count() > 0)():
        punishment.is_deleted = True
        await punishment.asave()
    else:
        await punishment.adelete()

    await callback.answer(_("Deleted"))
    await dialog.delete_message(callback.message.message_id)

    await dialog.edit_keyboard(dialog.data["main_message_id"], punishments, menu_data={"chat_member": member})


@punishment_deletion_router.callback_query(ButtonFilter(refuse))
async def refuse_deletion(callback: CallbackQuery, dialog: Dialog):
    await callback.answer(_("Ok"))
    await dialog.delete_message(callback.message.message_id)

