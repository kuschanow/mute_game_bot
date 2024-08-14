from aiogram.types import Chat as TeleChat

from bot.models.ChatMember import Chat


class ChatService:
    def __init__(self, chat_instance: Chat):
        self.instance = chat_instance

    @staticmethod
    async def get_or_create_chat(tele_chat: TeleChat) -> Chat:
        chat = (await Chat.objects.aget_or_create(id=tele_chat.id))[0]

        chat.name = tele_chat.full_name
        chat.type = tele_chat.type
        await chat.asave()

        return chat
