from aiogram import Router

from .common import common_router
from .games import games_router
from .punishment import punishment_router
from .warnings import warnings_router

handlers_router = Router()

handlers_router.include_routers(games_router, punishment_router, common_router, warnings_router)


