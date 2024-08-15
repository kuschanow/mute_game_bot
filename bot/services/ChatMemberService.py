from aiogram.types import Chat as TeleChat, ChatMemberAdministrator
from aiogram.enums.chat_type import ChatType

from bot.models import User, ChatMember
from bot.services.ChatService import ChatService


class ChatMemberService:
    def __init__(self, member_instance: ChatMember):
        self.instance = member_instance

    @staticmethod
    async def get_or_create_member(user: User, tele_chat: TeleChat) -> ChatMember:
        chat = await ChatService.get_or_create_chat(tele_chat)
        member = (await ChatMember.objects.aget_or_create(user=user, chat=chat))[0]

        if chat.type != ChatType.PRIVATE:
            tele_member = await tele_chat.get_member(user.id)
            member.is_admin = isinstance(tele_member, ChatMemberAdministrator)
        await member.asave()

        return member
