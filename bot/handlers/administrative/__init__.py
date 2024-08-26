from aiogram import Router

from .main_chat_settings import chat_settings_router

administrative_router = Router()

administrative_router.include_routers(chat_settings_router)