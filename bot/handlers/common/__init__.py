from aiogram import Router

from .start import start_router
from .help import help_router
from .private_game_commands import private_game_commands_router

common_router = Router()

common_router.include_routers(start_router, help_router, private_game_commands_router)

