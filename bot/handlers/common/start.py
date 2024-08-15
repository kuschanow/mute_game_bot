from aiogram import Router
from aiogram.filters.command import CommandStart
from aiogram.types import Message

from django.utils.translation import gettext as _
from django.conf import settings

start_router = Router()

@start_router.message(CommandStart())
async def start_command(message: Message):
    # Translators: start command answer
    text = _("Hi!\n"
             "I'm a bot that randomly gives out mutes in various games of luck.\n"
             "You can find out more by entering the command /%(help)s." % { "help": settings.HELP_COMMAND }
    )
    await message.answer(text=text)

