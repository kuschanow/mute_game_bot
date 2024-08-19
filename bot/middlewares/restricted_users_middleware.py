from typing import Callable, Dict, Any, Awaitable

from aiogram import Router
from aiogram.types import Message, CallbackQuery, ChatMemberRestricted, ChatMemberLeft


def set_restricted_user_middlewares(router: Router):
    router.message.outer_middleware.register(message_restricted_user_middleware)
    router.callback_query.outer_middleware.register(callback_restricted_user_middleware)

async def message_restricted_user_middleware(
        handler: Callable[[Message, Dict[str, Any]], Awaitable[Any]],
        message: Message,
        data: Dict[str, Any]
) -> Any:
    tele_member = await message.chat.get_member(message.from_user.id)
    if isinstance(tele_member, ChatMemberLeft):
        return
    return await handler(message, data)

async def callback_restricted_user_middleware(
        handler: Callable[[CallbackQuery, Dict[str, Any]], Awaitable[Any]],
        callback: CallbackQuery,
        data: Dict[str, Any]
) -> Any:
    tele_member = await callback.message.chat.get_member(callback.from_user.id)
    if isinstance(tele_member, ChatMemberRestricted):
        if not tele_member.can_send_messages:
            return
    return await handler(callback, data)

