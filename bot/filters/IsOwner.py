from aiogram.filters import Filter

from bot.models import ChatMember


class IsOwner(Filter):
    async def __call__(self, event, member: ChatMember) -> bool:
        return member.is_owner()
