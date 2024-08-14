from aiogram import Router

from .start import start_router

common_router = Router()

common_router.include_routers(start_router)

