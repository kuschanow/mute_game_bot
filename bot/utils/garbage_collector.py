from datetime import timedelta

from aiogram.enums import ChatType
from asgiref.sync import async_to_sync
from future.backports.datetime import datetime

from bot.generate_session import bot
from bot.models import Chat, ChatMember
from games.models import RandomChoiceGame
from shared import redis


def collect_garbage():
    for member in ChatMember.objects.exclude(chat__type=ChatType.PRIVATE.value):
        data = async_to_sync(redis.get_deserialized)(str(member.id))
        if "dialogs" in data:
            for key in data["dialogs"]:
                if "datetime" in data["dialogs"][key]:
                    if datetime.strptime(data["dialogs"][key]["datetime"], "%Y-%m-%d %H:%M:%S") + timedelta(days=1) < datetime.now():
                        if "message_id" in data["dialogs"][key]:
                            async_to_sync(bot.delete_message)(chat_id=member.chat.id, message_id=int(data["dialogs"][key]["message_id"]))
                        data["dialogs"].pop(key)
        async_to_sync(redis.set_serialized)(str(member.id), data)

    for game in RandomChoiceGame.objects.filter(created_at__lte=datetime.now() - timedelta(days=1), result__isnull=True):
        game_data = async_to_sync(redis.get_deserialized)(str(game.id))
        if "messages" in game_data:
            for message in game_data["messages"]:
                async_to_sync(bot.delete_message)(chat_id=game.creator.chat.id, message_id=int(message))

        async_to_sync(redis.delete)(str(game.id))
        game.delete()
