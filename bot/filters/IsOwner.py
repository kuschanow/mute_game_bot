from aiogram.filters import Filter
from django.conf import settings

from bot.models import ChatMember
from shared.enums import MemberStatus, InteractionLevel


class IsOwner(Filter):
    async def __call__(self, event, member: ChatMember) -> bool:
        return member.status == MemberStatus.OWNER.value or member.user_id in settings.ADMINS
