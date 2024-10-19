import re

from aiogram import Router
from aiogram.filters import Command, or_f
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message
from aiogram_dialog_manager import Dialog, DialogManager
from aiogram_dialog_manager.filter import DialogFilter, ButtonFilter
from aiogram_dialog_manager.instance import ButtonInstance
from asgiref.sync import sync_to_async
from django.conf import settings

from bot.dialogs.dialog_buttons import change_page, member_access_settings
from bot.dialogs.dialog_menus import access_groups, access_settings
from bot.dialogs.dialog_texts import access_settings_texts
from bot.filters import IsOwner, IsSuperAdmin
from bot.handlers.administrative.access_settings.utils import select_settings_target
from bot.models import Chat, AccessSettings, ChatMember
from bot.utils import get_member_from_message
from shared.enums import SettingsTarget

member_access_settings_router = Router()
member_access_settings_router.callback_query.filter(DialogFilter("access_settings"), or_f(IsOwner(), IsSuperAdmin()))
member_access_settings_router.message.filter(or_f(IsOwner(), IsSuperAdmin()))


@member_access_settings_router.callback_query(ButtonFilter(change_page))
async def select_page(callback: CallbackQuery, dialog: Dialog, button: ButtonInstance, state: FSMContext):
    await callback.answer()
    await dialog.remove_state(context=state)

    dialog.data["page"] = button.data["page"]

    await dialog.edit_keyboard(callback.message.message_id, access_groups)


@member_access_settings_router.callback_query(ButtonFilter(member_access_settings))
async def change_settings(callback: CallbackQuery, chat: Chat, button: ButtonInstance, dialog: Dialog):
    await callback.answer()
    await select_settings_target(callback, chat, dialog, button.data["id"], SettingsTarget.MEMBER.value, button.data["name"])


@member_access_settings_router.message(Command(settings.ADD_MEMBER_EXCEPTION_COMMAND))
async def add_to_group(message: Message, chat: Chat, dialog_manager: DialogManager, member: ChatMember, bot):
    pattern = r"(?: (\d+)| @(\w+))?$"
    match = re.search(pattern, message.text)

    if match:
        user_id, username = match.groups()

        target_member = await get_member_from_message(message, user_id, username)
    else:
        raise ValueError("Message text does not match the expected format.")

    query = AccessSettings.objects.filter(chat=chat, target=SettingsTarget.MEMBER.value, target_id=target_member.id)

    if not await query.aexists():
        reference = await sync_to_async(
            lambda: AccessSettings.objects.get(chat=chat, target=SettingsTarget.CHAT.value, target_id=chat.id).settings_object)()

        settings_object = reference
        settings_object.pk = None
        await settings_object.asave()

        await AccessSettings(chat=chat, target=SettingsTarget.MEMBER.value, target_id=target_member.id, settings_object=settings_object).asave()
    else:
        settings_object = await sync_to_async(lambda: query.first().settings_object)()

    dialog = Dialog.create("access_settings", user_id=member.user_id, chat_id=member.chat_id, bot=bot)

    dialog.data["is_super_admin"] = member.is_super_admin()
    dialog.data["target"] = SettingsTarget.MEMBER.value
    dialog.data["target_name"] = await sync_to_async(lambda: target_member.get_string())()
    dialog.data["page"] = 0
    dialog.data["add_member_exception_command"] = settings.ADD_MEMBER_EXCEPTION_COMMAND

    bot_message = await dialog.send_message(access_settings_texts["base_settings"], access_settings, menu_data={"settings_object": settings_object})
    dialog.data["main_message_id"] = bot_message.message_id
    await dialog_manager.save_dialog(dialog)

    await message.delete()

    dialog.data["settings_object_id"] = str(settings_object.id)
