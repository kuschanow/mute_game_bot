from aiogram import Router
from aiogram_dialog_manager import DialogManager

from bot.generate_session import bot
from .dialog_prototypes import prototypes
from .punishment_creation import punishment_creation_router
from .punishment_deletion import punishment_deletion_router
from shared import dialog_storage

punishment_router = Router()

punishment_dialog_manager = DialogManager(storage=dialog_storage, router=punishment_router, bot=bot, prototypes=prototypes)

punishment_router.include_routers(punishment_creation_router, punishment_deletion_router)
