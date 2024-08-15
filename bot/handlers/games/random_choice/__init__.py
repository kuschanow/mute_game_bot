from .game_creation_handlers import game_handlers_router

from aiogram import Router

random_choice_game_router = Router()

random_choice_game_router.include_routers(game_handlers_router)
