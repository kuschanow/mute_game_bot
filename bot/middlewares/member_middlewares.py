from typing import Callable, Dict, Any, Awaitable

from aiogram import Router
from aiogram.types import Message, CallbackQuery

from bot.models import ChatMember


def set_member_middlewares(router: Router):
    router.message.outer_middleware.register(message_member_middleware)
    router.callback_query.outer_middleware.register(callback_member_middleware)

async def message_member_middleware(
        handler: Callable[[Message, Dict[str, Any]], Awaitable[Any]],
        message: Message,
        data: Dict[str, Any]
) -> Any:
    data["member"] = await ChatMember.get_or_create_member(data["user"], message.chat)
    return await handler(message, data)

async def callback_member_middleware(
        handler: Callable[[CallbackQuery, Dict[str, Any]], Awaitable[Any]],
        callback: CallbackQuery,
        data: Dict[str, Any]
) -> Any:
    data["member"] = await ChatMember.get_or_create_member(data["user"], callback.message.chat)
    return await handler(callback, data)

