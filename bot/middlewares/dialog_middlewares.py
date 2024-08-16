from datetime import datetime, timedelta
from typing import Callable, Dict, Any, Awaitable

from aiogram import Router
from aiogram.types import Message


def set_dialog_middlewares(router: Router):
    router.message.middleware.register(message_dialog_middleware)

async def message_dialog_middleware(
        handler: Callable[[Message, Dict[str, Any]], Awaitable[Any]],
        message: Message,
        data: Dict[str, Any]
) -> Any:
    user_data = await data['state'].get_data()
    if "dialogs" in user_data:
        for d in list(user_data["dialogs"].keys()):
            if datetime.strptime(user_data["dialogs"][d]["datetime"], "%Y-%m-%d %H:%M:%S.%f") + timedelta(days=1) < datetime.now():
                user_data["dialogs"].pop(d)

    await data['state'].set_data(user_data)

    return await handler(message, data)
