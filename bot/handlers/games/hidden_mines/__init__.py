from aiogram_dialog_manager import DialogManager
from aiogram_dialog_manager.filter import DialogFilter

from bot.generate_session import bot
from .game_creation_handlers import game_creation_router
from shared import dialog_storage

from aiogram import Router

hidden_mines_game_router = Router()
hidden_mines_game_router.callback_query.filter(DialogFilter("hidden_mines_game_creation", "hidden_mines_game"))

random_choice_game_dialog_manager = DialogManager(storage=dialog_storage, router=hidden_mines_game_router, bot=bot)

hidden_mines_game_router.include_routers(game_creation_router)
