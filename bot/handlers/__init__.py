from aiogram import Router

from .common import common_router
from .games import games_router

handlers_router = Router()

handlers_router.include_routers(games_router, common_router)


