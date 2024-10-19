from aiogram import Router
from aiogram_dialog_manager import DialogManager
from aiogram_dialog_manager.filter import DialogFilter

from bot.generate_session import bot
from shared import dialog_storage
from .access_settings import access_settings_router

administrative_router = Router()
administrative_router.callback_query.filter(DialogFilter("access_settings"))

administrative_dialog_manager = DialogManager(storage=dialog_storage, router=administrative_router, bot=bot)

administrative_router.include_routers(access_settings_router)
