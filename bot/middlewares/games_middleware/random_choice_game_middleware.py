from typing import Callable, Dict, Any, Awaitable

from aiogram import Router
from aiogram.types import CallbackQuery, Message, TelegramObject
from asgiref.sync import sync_to_async, async_to_sync

from games.models import RandomChoiceGame


def set_random_choice_game_middlewares(router: Router):
    router.callback_query.middleware.register(game_middleware)
    router.message.middleware.register(game_middleware)

async def game_middleware(
        handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: Dict[str, Any]
) -> Any:
    if "dialog" in data and "game_id" in data["dialog"].values:
        data["game"] = await RandomChoiceGame.objects.aget(id=data["dialog"].values["game_id"])

    return await handler(event, data)
