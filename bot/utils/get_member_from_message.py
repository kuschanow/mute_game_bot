from aiogram.types import Message

from bot.models import ChatMember


async def get_member_from_message(message: Message, user_id: str, username: str) -> ChatMember | None:
    user_identifier = (
        {"user_id": message.reply_to_message.from_user.id}
        if message.reply_to_message
        else {"user_id": int(user_id)} if user_id
        else {"user__username": username} if username
        else {}
    )

    if user_identifier:
        return await ChatMember.objects.aget(chat_id=message.chat.id, **user_identifier)
    else:
        return None