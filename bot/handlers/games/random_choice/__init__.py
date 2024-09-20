from aiogram_dialog_manager import DialogManager
from aiogram_dialog_manager.filter import DialogFilter

from bot.generate_session import bot
from .game_creation_handlers import game_creation_router
from .game_handlers import game_router
from shared import dialog_storage

from aiogram import Router

random_choice_game_router = Router()
random_choice_game_router.callback_query.filter(DialogFilter("random_choice_game_creation", "random_choice_game"))

random_choice_game_dialog_manager = DialogManager(storage=dialog_storage, router=random_choice_game_router, bot=bot)

random_choice_game_router.include_routers(game_creation_router, game_router)
