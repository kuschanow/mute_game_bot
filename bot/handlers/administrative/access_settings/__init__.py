from aiogram import Router
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery
from aiogram_dialog_manager import Dialog, DialogManager
from aiogram_dialog_manager.filter import DialogFilter, ButtonFilter

from bot.utils.dialog.dialog_buttons import cancel
from .games_settings import games_settings_router
from .main_access_settings import main_access_settings_router

access_settings_router = Router()
access_settings_router.callback_query.filter(DialogFilter("access_settings"))

access_settings_router.include_routers(games_settings_router, main_access_settings_router)

@access_settings_router.callback_query(ButtonFilter(cancel))
async def cancel(callback: CallbackQuery, state: FSMContext, dialog: Dialog, dialog_manager: DialogManager):
    await callback.answer()
    await dialog.remove_state(context=state)
    await dialog.delete_all_messages()
    await dialog_manager.delete_dialog(dialog)
