from aiogram.types import User as TeleUser, Chat as TeleChat

from bot.models import User
from bot.services.ChatMemberService import ChatMemberService


class UserService:
    def __init__(self, user_instance: User):
        self.instance = user_instance

    @staticmethod
    async def get_or_create_user(tele_user: TeleUser, chat: TeleChat) -> User:
        user = (await User.objects.aget_or_create(id=tele_user.id))[0]

        user.username = tele_user.username
        user.first_name = tele_user.first_name
        user.last_name = tele_user.last_name
        await user.asave()

        await ChatMemberService.get_or_create_member(user, chat)

        return user
