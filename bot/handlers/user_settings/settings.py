from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message, CallbackQuery
from aiogram_dialog_manager import DialogManager, Dialog
from aiogram_dialog_manager.filter import ButtonFilter
from aiogram_dialog_manager.instance import ButtonInstance
from asgiref.sync import sync_to_async
from django.conf import settings

from bot.generate_session import bot
from bot.models import ChatMember
from bot.dialogs.dialog_buttons import ping_in_stats, make_diff, reset_to_global
from bot.dialogs.dialog_menus import user_settings
from bot.dialogs.dialog_texts import user_settings_texts

settings_router = Router()


@settings_router.message(Command(settings.USER_SETTINGS_COMMAND))
async def user_settings_command(message: Message, member: ChatMember, dialog_manager: DialogManager):
    dialog = Dialog.create("user_settings", user_id=member.user_id, chat_id=member.chat_id, bot=bot)

    dialog.data["settings_type"] = "global" if member.user_id == member.chat_id else "local"

    settings_object = await sync_to_async(lambda: member.user.global_settings if member.user_id == member.chat_id else member.local_settings)()
    await dialog.send_message(user_settings_texts[dialog.data["settings_type"]], user_settings, menu_data={"settings_object": settings_object})

    await dialog_manager.save_dialog(dialog)

    await message.delete()


@settings_router.callback_query(ButtonFilter(make_diff))
async def make_diff(callback: CallbackQuery, member: ChatMember, dialog: Dialog):
    await callback.answer()

    global_settings = await sync_to_async(lambda: member.user.global_settings)()
    local_settings = global_settings
    local_settings.pk = None
    await local_settings.asave()
    member.local_settings_id = local_settings.id
    await member.asave()

    await dialog.edit_keyboard(callback.message.message_id, user_settings, menu_data={"settings_object": local_settings})


@settings_router.callback_query(ButtonFilter(reset_to_global))
async def clear_settings(callback: CallbackQuery, member: ChatMember, dialog: Dialog):
    await callback.answer()

    await sync_to_async(lambda: member.local_settings.delete())()

    await dialog.edit_keyboard(callback.message.message_id, user_settings, menu_data={"settings_object": None})


@settings_router.callback_query(ButtonFilter(ping_in_stats))
async def main_settings(callback: CallbackQuery, member: ChatMember, dialog: Dialog, button: ButtonInstance):
    await callback.answer()

    settings_object = await sync_to_async(lambda: member.user.global_settings if member.user_id == member.chat_id else member.local_settings)()

    current_value = getattr(settings_object, button.type_name)
    setattr(settings_object, button.type_name, not current_value)

    await settings_object.asave()

    await dialog.edit_keyboard(
        callback.message.message_id,
        user_settings,
        menu_data={"settings_object": settings_object}
    )
