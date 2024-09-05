from typing import Callable, Dict, Any, Awaitable

from aiogram import Router
from aiogram.types import Message, CallbackQuery

from bot.logger import logger
from bot.models import User


def set_logger_middlewares(router: Router):
    router.message.outer_middleware.register(message_logger_middleware)
    router.callback_query.outer_middleware.register(callback_logger_middleware)

async def message_logger_middleware(
        handler: Callable[[Message, Dict[str, Any]], Awaitable[Any]],
        message: Message,
        data: Dict[str, Any]
) -> Any:
    logger.info("Receive message from user: %(user_id)s in chat: %(chat_id)s" % {"user_id": data["user"].id, "chat_id": data["chat"].id},
                message_text=message.text,
                user=data["user"],
                chat=data["chat"],
                chat_member=data["member"],
                settings=data["member_settings"])
    try:
        return await handler(message, data)
    except Exception as e:
        logger.error(e,
                     user=data["user"],
                     chat=data["chat"],
                     chat_member=data["member"],
                     settings=data["member_settings"])

async def callback_logger_middleware(
        handler: Callable[[CallbackQuery, Dict[str, Any]], Awaitable[Any]],
        callback: CallbackQuery,
        data: Dict[str, Any]
) -> Any:
    logger.info("Receive callback from user: %(user_id)s in chat: %(chat_id)s" % {"user_id": data["user"].id, "chat_id": data["chat"].id},
                callback_data=callback.data,
                user=data["user"],
                chat=data["chat"],
                chat_member=data["member"],
                settings=data["member_settings"])
    try:
        return await handler(callback, data)
    except Exception as e:
        logger.error(e,
                     user=data["user"],
                     chat=data["chat"],
                     chat_member=data["member"],
                     settings=data["member_settings"])

