from aiogram import Router

from .hidden_mines import hidden_mines_game_router
from .punishment_selection_handlers import punishment_selection_router
from .random_choice import random_choice_game_router

games_router = Router()

games_router.include_routers(punishment_selection_router, random_choice_game_router, hidden_mines_game_router)
