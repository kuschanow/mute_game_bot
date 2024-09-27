import re

from aiogram import Router, F
from aiogram.enums.chat_type import ChatType
from aiogram.filters import Command, MagicData
from aiogram.types import Message
from django.conf import settings

from bot.handlers.stats.utils.stats import get_random_choice_game_detailed_stats_by_user
from bot.handlers.stats.utils.texts import get_detailed_text_by_member
from bot.models import ChatMember

user_stats_router = Router()
user_stats_router.message.filter(MagicData(F.chat.type.is_not(ChatType.PRIVATE)))


@user_stats_router.message(Command(settings.SHOW_USER_STATS_COMMAND))
async def chat_stats_command(message: Message, member: ChatMember):
    member_for_stats = member

    match = re.search(rf"/{settings.SHOW_USER_STATS_COMMAND} @([a-zA-Z0-9]+)|(\d+)", message.text)

    if message.reply_to_message is not None:
        member_for_stats = await ChatMember.objects.aget(chat_id=member.chat_id, user_id=message.reply_to_message.from_user.id)
    elif match:
        groups = match.groups()
        if groups[0]:
            member_for_stats = await ChatMember.objects.aget(chat_id=member.chat_id, user__username=groups[0])
        elif groups[1]:
            member_for_stats = await ChatMember.objects.aget(chat_id=member.chat_id, user_id=int(groups[1]))

    await message.answer(text=await get_detailed_text_by_member(await get_random_choice_game_detailed_stats_by_user(member_for_stats), member_for_stats))

    await message.delete()


