from aiogram import Router
from aiogram.filters.command import Command
from aiogram.types import Message
from django.conf import settings
from django.utils.translation import gettext as _

private_game_commands_router = Router()


@private_game_commands_router.message(Command(settings.RANDOM_CHOICE_GAME_COMMAND))
@private_game_commands_router.message(Command(settings.CREATE_PUNISHMENT_COMMAND))
async def private_game_command(message: Message):
    # Translators: wrong game command answer
    await message.answer(text=_("Can't start game in private chat"))

