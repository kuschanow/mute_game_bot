from aiogram import Router

from .start import start_router
from .help import help_router
from .wrong_private_commands import wrong_private_commands_router

common_router = Router()

common_router.include_routers(start_router, help_router, wrong_private_commands_router)

