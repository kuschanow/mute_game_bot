from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import Message, CallbackQuery
from django.conf import settings

from bot.filters import IsOwner
from bot.models import Chat
from .utils.chat_settings_keyboards import get_chat_settings_keyboard
from django.utils.translation import gettext as _

chat_settings_router = Router()
chat_settings_router.callback_query.filter(F.data.startswith("chat_settings"), IsOwner())
chat_settings_router.message.filter(IsOwner())


@chat_settings_router.message(Command(settings.CHAT_SETTINGS_COMMAND))
async def chat_settings_command(message: Message, chat: Chat):
    await message.answer(text=_("Chat settings"), reply_markup=get_chat_settings_keyboard(chat))
    await message.delete()


@chat_settings_router.callback_query()
async def chat_settings(callback: CallbackQuery, chat: Chat):
    if "can_admins_join_games" in callback.data:
        chat.can_admins_join_games = not chat.can_admins_join_games
    if "can_admins_create_games" in callback.data:
        chat.can_admins_create_games = not chat.can_admins_create_games
    if "can_admins_press_other_buttons" in callback.data:
        chat.can_admins_press_other_buttons = not chat.can_admins_press_other_buttons
    if "can_admins_ignore_time_limitations" in callback.data:
        chat.can_admins_ignore_time_limitations = not chat.can_admins_ignore_time_limitations
    if "can_members_create_public_punishments" in callback.data:
        chat.can_members_create_public_punishments = not chat.can_members_create_public_punishments

    await chat.asave()

    await callback.message.edit_text(text=_("Chat settings"), reply_markup=get_chat_settings_keyboard(chat))
    await callback.answer()

