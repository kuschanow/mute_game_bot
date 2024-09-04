from aiogram import Router, F
from aiogram.enums import ChatType
from aiogram.filters.command import Command
from aiogram.types import Message
from django.conf import settings
from django.utils.translation import gettext as _

from bot.logger import logger
from bot.models import Chat

wrong_private_commands_router = Router()
wrong_private_commands_router.message.filter(F.chat.type.is_(ChatType.PRIVATE))


@wrong_private_commands_router.message(Command(settings.RANDOM_CHOICE_GAME_COMMAND))
@wrong_private_commands_router.message(Command(settings.CREATE_PUNISHMENT_COMMAND))
@wrong_private_commands_router.message(Command(settings.ACCESS_SETTINGS_COMMAND))
@wrong_private_commands_router.message(Command(settings.CHAT_SETTINGS_COMMAND))
@wrong_private_commands_router.message(Command(settings.SHOW_CHAT_STATS_COMMAND))
@wrong_private_commands_router.message(Command(settings.SHOW_USER_STATS_COMMAND))
async def private_game_command(message: Message, chat: Chat):
    logger.info("Receive wrong %(command)s" % {"command": message.text}, chat=chat)
    await message.answer(text=_("Can't use this in private chat"))

