from aiogram import Router, F
from aiogram_dialog_manager import DialogManager

from .chat_stats import chat_stats_router
from shared import dialog_storage
from bot.generate_session import bot
from .dialog_prototypes import prototypes

stats_router = Router()

stats_dialog_manager = DialogManager(storage=dialog_storage, router=stats_router, bot=bot, prototypes=prototypes)

stats_router.callback_query.filter(F.data.startswith("stats"))
stats_router.include_routers(chat_stats_router)
