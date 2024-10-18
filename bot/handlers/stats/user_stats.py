import re

from aiogram import Router, F
from aiogram.enums.chat_type import ChatType
from aiogram.filters import Command, MagicData
from aiogram.types import Message
from django.conf import settings

from bot.handlers.stats.utils.stats import get_random_choice_game_detailed_stats_by_user
from bot.handlers.stats.utils.texts import get_detailed_text_by_member
from bot.models import ChatMember
from bot.utils import get_member_from_message

user_stats_router = Router()
user_stats_router.message.filter(MagicData(F.chat.type.is_not(ChatType.PRIVATE)))


@user_stats_router.message(Command(settings.SHOW_USER_STATS_COMMAND))
async def chat_stats_command(message: Message, member: ChatMember):
    member_for_stats = member

    pattern = r"(\d+)| @(\w+)?$"
    match = re.search(pattern, message.text)

    if match:
        user_id, username = match.groups()
        member_for_stats = await get_member_from_message(message, user_id, username)

    await message.answer(text=await get_detailed_text_by_member(await get_random_choice_game_detailed_stats_by_user(member_for_stats), member_for_stats))

    await message.delete()


