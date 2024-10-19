from aiogram import Router
from aiogram.types import CallbackQuery
from aiogram_dialog_manager import DialogManager, Dialog
from aiogram_dialog_manager.filter import DialogFilter, ButtonFilter

from bot.generate_session import bot
from shared import dialog_storage
from .settings import settings_router

user_settings_router = Router()
user_settings_router.callback_query.filter(DialogFilter("user_settings"))

user_setting_dialog_manager = DialogManager(storage=dialog_storage, router=user_settings_router, bot=bot)

user_settings_router.include_routers(settings_router)


@user_settings_router.callback_query(ButtonFilter("cancel"))
async def cancel(callback: CallbackQuery, dialog: Dialog, dialog_manager: DialogManager):
    await callback.answer()
    await dialog.delete_all_messages()
    await dialog_manager.delete_dialog(dialog)
