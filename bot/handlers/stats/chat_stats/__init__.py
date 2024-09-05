from aiogram import Router, F

from .stats_command_handler import stats_command_router
from .chat_stats_details_handlers import chat_stats_detailed_router
from .chat_stats_top_handlers import chat_stats_top_router

chat_stats_router = Router()
chat_stats_router.callback_query.filter(F.data.startswith("stats:chat"))
chat_stats_router.include_routers(stats_command_router, chat_stats_top_router, chat_stats_detailed_router)
