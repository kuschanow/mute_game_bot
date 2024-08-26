from aiogram.filters import Filter
from django.conf import settings

from bot.models import ChatMember
from shared.enums import MemberStatus, InteractionLevel


class IsAdmin(Filter):
    async def __call__(self, event, member: ChatMember) -> bool:
        return member.is_admin()
