from aiogram import Router, F
from aiogram.enums import ChatType
from aiogram.filters.command import Command
from aiogram.types import Message
from django.conf import settings
from django.utils.translation import gettext as _

private_game_commands_router = Router()
private_game_commands_router.message.filter(F.chat.type.is_(ChatType.PRIVATE))


@private_game_commands_router.message(Command(settings.RANDOM_CHOICE_GAME_COMMAND))
@private_game_commands_router.message(Command(settings.CREATE_PUNISHMENT_COMMAND))
async def private_game_command(message: Message):
    # Translators: wrong command answer
    await message.answer(text=_("Can't use this in private chat"))

