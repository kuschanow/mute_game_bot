from aiogram.filters import Filter

from bot.models import ChatMember


class IsRestricted(Filter):
    async def __call__(self, event, member: ChatMember) -> bool:
        return not member.can_interact
