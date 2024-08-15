from aiogram import Router
from .punishment_creation import punishment_creation_router

punishment_router = Router()

punishment_router.include_routers(punishment_creation_router)
