from aiogram.filters import Filter

from bot.models import ChatMember


class IsGameCreator(Filter):
    async def __call__(self, event, game, member: ChatMember) -> bool:
        return game.creator_id == member.id
