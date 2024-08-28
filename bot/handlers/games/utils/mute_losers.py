from datetime import datetime

from aiogram.types import ChatPermissions
from asgiref.sync import sync_to_async
from django.conf import settings

from bot.generate_session import bot
from bot.models import Chat


async def mute_losers(game, result, chat: Chat):
    time = await sync_to_async(lambda: game.punishment.time)()
    for loser in await sync_to_async(lambda: list(result.losers.all()))():
        user_id = await sync_to_async(lambda: loser.chat_member.user_id)()
        if user_id in settings.ADMINS:
            continue

        try:
            await bot.restrict_chat_member(
                chat_id=chat.id,
                user_id=user_id,
                permissions=ChatPermissions(can_send_messages=False),
                until_date=datetime.now() + time
            )
        except:
            pass