from aiogram.filters import Filter
from aiogram.types import CallbackQuery

from bot.models import ChatMember
from shared import redis


class DialogAccess(Filter):
    async def __call__(self, callback_query: CallbackQuery, member: ChatMember) -> bool:
        data = await redis.get_deserialized(str(member.id))
        if data is None or "dialogs" not in data:
            return False
        return str(callback_query.message.message_id) in data["dialogs"]
