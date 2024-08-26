from aiogram import Router

from .main_chat_settings import main_access_settings_router

access_settings_router = Router()

access_settings_router.include_routers(main_access_settings_router)
