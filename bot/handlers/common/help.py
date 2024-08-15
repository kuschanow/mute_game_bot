from aiogram import Router
from aiogram.filters.command import Command
from aiogram.types import Message

from django.utils.translation import gettext as _
from django.conf import settings

help_router = Router()

@help_router.message(Command(settings.HELP_COMMAND))
async def help_command(message: Message):
    # Translators: help command answer
    text = _("This is basic text, replace it to suit your needs")
    await message.answer(text=text)

