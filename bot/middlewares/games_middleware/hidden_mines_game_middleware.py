from typing import Callable, Dict, Any, Awaitable

from aiogram import Router
from aiogram.types import TelegramObject

from games.models import RandomChoiceGame, HiddenMinesGame


def set_hidden_mines_game_middlewares(router: Router):
    router.callback_query.middleware.register(game_middleware)
    router.message.middleware.register(game_middleware)


async def game_middleware(
        handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: Dict[str, Any]
) -> Any:
    if "dialog" in data and "game_id" in data["dialog"].values:
        data["game"] = await HiddenMinesGame.objects.aget(id=data["dialog"].values["game_id"])
        data["dialog"].values["game"] = data.get("game")

    return await handler(event, data)
