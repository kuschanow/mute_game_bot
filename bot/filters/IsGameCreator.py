from aiogram.filters import Filter
from django.conf import settings

from bot.models import ChatMember
from shared.enums import MemberStatus, InteractionLevel


class IsGameCreator(Filter):
    async def __call__(self, event, game, member: ChatMember) -> bool:
        return game.creator_id == member.id
