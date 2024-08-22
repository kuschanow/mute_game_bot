from aiogram.filters import Filter
from django.conf import settings

from bot.models import ChatMember


class IsSuperAdmin(Filter):
    async def __call__(self, event, user: ChatMember) -> bool:
        return user.id in settings.ADMINS
