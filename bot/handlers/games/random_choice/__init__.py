from .game_creation_handlers import game_creation_router
from .game_handlers import game_router

from aiogram import Router

random_choice_game_router = Router()

random_choice_game_router.include_routers(game_creation_router, game_router)
