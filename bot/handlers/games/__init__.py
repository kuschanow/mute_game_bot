from aiogram import Router

from .random_choice import random_choice_game_router

games_router = Router()

games_router.include_routers(random_choice_game_router)
