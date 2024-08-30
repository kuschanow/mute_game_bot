from aiogram import Router, F

from .chat_stats import chat_stats_router

stats_router = Router()
stats_router.callback_query.filter(F.data.startswith("stats"))
stats_router.include_routers(chat_stats_router)
