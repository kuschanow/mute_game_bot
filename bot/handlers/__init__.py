from aiogram import Router
from aiogram.filters import invert_f

from .administrative import administrative_router
from .common import common_router
from .games import games_router
from .punishment import punishment_router
from .stats import stats_router
from .unhandled import unhandled_router
from ..filters import IsRestricted

handlers_router = Router()
handlers_router.message.filter(invert_f(IsRestricted()))
handlers_router.callback_query.filter(invert_f(IsRestricted()))


handlers_router.include_routers(administrative_router, games_router, punishment_router, stats_router, common_router, unhandled_router)


