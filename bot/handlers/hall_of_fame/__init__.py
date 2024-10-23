from aiogram import Router, F
from aiogram.filters import or_f, MagicData
from aiogram.types import CallbackQuery
from aiogram_dialog_manager import DialogManager, Dialog
from aiogram_dialog_manager.filter import DialogFilter, DialogAccessFilter, ButtonFilter

from bot.generate_session import bot
from shared import dialog_storage
from .hall_of_fame import hall_of_fame_board_router

hall_of_fame_router = Router()
hall_of_fame_router.include_routers(hall_of_fame_board_router)

hall_of_fame_router.callback_query.filter(DialogFilter("hall_of_fame"))

hall_of_fame_dialog_manager = DialogManager(storage=dialog_storage, router=hall_of_fame_router, bot=bot)


@hall_of_fame_router.callback_query(ButtonFilter("cancel"), or_f(DialogAccessFilter(), MagicData(F.access_settings.can_press_other_buttons)))
async def cancel(callback: CallbackQuery, dialog: Dialog, dialog_manager: DialogManager):
    await callback.answer()
    await dialog.delete_all_messages()
    await dialog_manager.delete_dialog(dialog)
