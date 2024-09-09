from aiogram import Router

from .main_access_settings import main_access_settings_router
from .games_settings import games_settings_router

access_settings_router = Router()

access_settings_router.include_routers(games_settings_router, main_access_settings_router)
