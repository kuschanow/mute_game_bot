from aiogram import Router

from aiogram_dialog_manager import DialogManager
from shared import dialog_storage
from bot.generate_session import bot

from .access_settings import access_settings_router

administrative_router = Router()

administrative_dialog_manager = DialogManager(storage=dialog_storage, router=administrative_router, bot=bot)

administrative_router.include_routers(access_settings_router)