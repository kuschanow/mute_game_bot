from typing import Callable, Dict, Any, Awaitable

from aiogram import Router
from aiogram.types import Message, CallbackQuery

from bot.services.ChatService import ChatService


def set_chat_middlewares(router: Router):
    router.message.outer_middleware.register(message_chat_middleware)
    router.callback_query.outer_middleware.register(callback_chat_middleware)

async def message_chat_middleware(
        handler: Callable[[Message, Dict[str, Any]], Awaitable[Any]],
        message: Message,
        data: Dict[str, Any]
) -> Any:
    data["chat"] = await ChatService.get_or_create_chat(message.chat)
    return await handler(message, data)

async def callback_chat_middleware(
        handler: Callable[[CallbackQuery, Dict[str, Any]], Awaitable[Any]],
        callback: CallbackQuery,
        data: Dict[str, Any]
) -> Any:
    data["chat"] = await ChatService.get_or_create_chat(callback.message.chat)
    return await handler(callback, data)

