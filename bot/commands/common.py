from aiogram import Bot
from aiogram.types import BotCommand
from django.conf import settings
from django.utils.translation import gettext as _


commands = [
    BotCommand(command=f"/{settings.HELP_COMMAND}", description=_("Show help information")),
    BotCommand(command=f"/{settings.RANDOM_CHOICE_GAME_COMMAND}", description=_("Start a random choice game")),
    BotCommand(command=f"/{settings.CREATE_PUNISHMENT_COMMAND}", description=_("Create new punishment")),
    BotCommand(command=f"/{settings.SHOW_USER_STATS_COMMAND}", description=_("Display user statistics")),
    BotCommand(command=f"/{settings.SHOW_CHAT_STATS_COMMAND}", description=_("Display current chat statistics")),
    BotCommand(command=f"/{settings.USER_SETTINGS_COMMAND}", description=_("Change private bot settings")),
    BotCommand(command=f"/{settings.DELETE_PUNISHMENT_COMMAND}", description=_("Delete punishments")),
    BotCommand(command=f"/{settings.ACCESS_SETTINGS_COMMAND}", description=_("Change access settings for current chat")),
    # # Translators: chat settings command hint
    # BotCommand(command=f"/{settings.CHAT_SETTINGS_COMMAND}", description=_("Change bot settings for current chat")),
]

async def set_default_commands(bot: Bot):
    await bot.set_my_commands(commands)


