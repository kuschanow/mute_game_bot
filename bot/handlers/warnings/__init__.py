from aiogram import Router

from .no_access import no_access_router
from .unhandled import unhandled_router

warnings_router = Router()

warnings_router.include_routers(no_access_router, unhandled_router)


