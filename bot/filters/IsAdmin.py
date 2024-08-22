from aiogram.filters import Filter
from django.conf import settings

from bot.models import ChatMember
from shared.enums import MemberStatus, InteractionLevel


class IsAdmin(Filter):
    async def __call__(self, event, member: ChatMember) -> bool:
        return (member.status in [MemberStatus.ADMIN.value, MemberStatus.OWNER.value]
                or member.interaction_level == InteractionLevel.CAN_ADMINISTRATE.value
                or member.user_id in settings.ADMINS)
