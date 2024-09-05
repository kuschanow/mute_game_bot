from typing import Callable, Dict, Any, Awaitable

from aiogram import Router
from aiogram.types import Message, CallbackQuery

from bot.models import User


def set_user_middlewares(router: Router):
    router.message.outer_middleware.register(message_user_middleware)
    router.callback_query.outer_middleware.register(callback_user_middleware)

async def message_user_middleware(
        handler: Callable[[Message, Dict[str, Any]], Awaitable[Any]],
        message: Message,
        data: Dict[str, Any]
) -> Any:
    data["user"] = await User.get_or_create_user(message.from_user, message.chat)
    return await handler(message, data)

async def callback_user_middleware(
        handler: Callable[[CallbackQuery, Dict[str, Any]], Awaitable[Any]],
        callback: CallbackQuery,
        data: Dict[str, Any]
) -> Any:
    data["user"] = await User.get_or_create_user(callback.from_user, callback.message.chat)
    return await handler(callback, data)

