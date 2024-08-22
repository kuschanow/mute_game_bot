from aiogram.filters import Filter

from bot.models import ChatMember
from shared.enums import InteractionLevel


class IsRestricted(Filter):
    async def __call__(self, event, member: ChatMember) -> bool:
        return member.interaction_level == InteractionLevel.RESTRICTED
