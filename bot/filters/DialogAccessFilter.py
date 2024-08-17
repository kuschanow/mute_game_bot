from aiogram.filters import Filter
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery

from bot.models import ChatMember
from shared import redis


class DialogAccessFilter(Filter):
    async def __call__(self, callback_query: CallbackQuery, member: ChatMember) -> bool:
        data = await redis.get(str(member.id))
        if data is None or "dialogs" not in data:
            return False
        return callback_query.data.split(':')[-1] in data["dialogs"]
