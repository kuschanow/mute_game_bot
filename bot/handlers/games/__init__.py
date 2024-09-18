from aiogram import Router
from aiogram_dialog_manager import DialogManager

from .dialog_prototypes import prototypes
from .random_choice import random_choice_game_router
from shared import dialog_storage
from bot.generate_session import bot

games_router = Router()

games_dialog_manager = DialogManager(storage=dialog_storage, router=games_router, bot=bot, prototypes=prototypes)

games_router.include_routers(random_choice_game_router)
