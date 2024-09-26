from aiogram import Router
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery
from aiogram_dialog_manager import Dialog
from aiogram_dialog_manager import DialogManager
from aiogram_dialog_manager.filter import DialogFilter, ButtonFilter

from bot.generate_session import bot
from bot.utils.dialog.dialog_buttons import cancel
from shared import dialog_storage
from .punishment_creation import punishment_creation_router
from .punishment_deletion import punishment_deletion_router

punishment_router = Router()
punishment_router.callback_query.filter(DialogFilter("punishment_creation", "punishment_deletion"))

punishment_dialog_manager = DialogManager(storage=dialog_storage, router=punishment_router, bot=bot)

punishment_router.include_routers(punishment_creation_router, punishment_deletion_router)


@punishment_router.callback_query(ButtonFilter(cancel))
async def cancel(callback: CallbackQuery, state: FSMContext, dialog: Dialog, dialog_manager: DialogManager):
    await callback.answer()
    await dialog.remove_state(context=state)
    await dialog.delete_all_messages()
    await dialog_manager.delete_dialog(dialog)
