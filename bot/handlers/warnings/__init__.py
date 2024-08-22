from aiogram import Router

from .unhandled import unhandled_router

warnings_router = Router()

warnings_router.include_routers(unhandled_router)


