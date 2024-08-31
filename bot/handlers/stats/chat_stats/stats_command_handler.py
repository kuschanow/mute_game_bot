import re
from datetime import datetime

from aiogram import Router, F
from aiogram.enums.chat_type import ChatType
from aiogram.filters import Command, MagicData
from aiogram.types import Message
from django.conf import settings

from bot.handlers.stats.chat_stats.utils.keyboards import get_top_stats_keyboard
from bot.handlers.stats.chat_stats.utils.stats import get_random_choice_game_time_stats, get_random_choice_game_detailed_stats_by_user
from bot.handlers.stats.chat_stats.utils.texts import get_top_time_text, get_detailed_text, get_detailed_text_by_member
from bot.models import Chat, ChatMember
from shared import redis

stats_command_router = Router()
stats_command_router.message.filter(MagicData(F.chat.type.is_not(ChatType.PRIVATE)))


@stats_command_router.message(Command(settings.SHOW_CHAT_STATS_COMMAND))
async def chat_stats_command(message: Message, chat: Chat, member: ChatMember):
    new_message = await message.answer(text=await get_top_time_text(await get_random_choice_game_time_stats(chat), 0),
                                       reply_markup=await get_top_stats_keyboard(chat, 0, "time"))

    data = await redis.get_deserialized(str(member.id))
    if "dialogs" not in data:
        data["dialogs"] = {str(new_message.message_id): {"datetime": str(datetime.utcnow())}}
    await redis.set_serialized(str(member.id), data)

    await message.delete()


@stats_command_router.message(Command(settings.SHOW_USER_STATS_COMMAND))
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


