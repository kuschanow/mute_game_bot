from aiogram import Router

from .access_settings import access_settings_router

administrative_router = Router()

administrative_router.include_routers(access_settings_router)