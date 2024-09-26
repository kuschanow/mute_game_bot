from aiogram import Router
from aiogram.types import CallbackQuery
from aiogram_dialog_manager import DialogManager, Dialog
from aiogram_dialog_manager.filter import DialogFilter, ButtonFilter

from bot.generate_session import bot
from bot.utils.dialog.dialog_buttons import cancel
from shared import dialog_storage
from .chat_stats import chat_stats_router
from .user_stats import user_stats_router

stats_router = Router()
stats_router.callback_query.filter(DialogFilter("chat_stats"))

chat_stats_dialog_manager = DialogManager(storage=dialog_storage, router=stats_router, bot=bot)

stats_router.include_routers(chat_stats_router, user_stats_router)


@stats_router.callback_query(ButtonFilter(cancel))
async def cancel(callback: CallbackQuery, dialog: Dialog, dialog_manager: DialogManager):
    await callback.answer()
    await dialog.delete_all_messages()
    await dialog_manager.delete_dialog(dialog)
