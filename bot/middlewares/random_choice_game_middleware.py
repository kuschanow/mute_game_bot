from typing import Callable, Dict, Any, Awaitable

from aiogram import Router
from aiogram.types import CallbackQuery

from games.models import RandomChoiceGame


def set_random_choice_game_middlewares(router: Router):
    router.callback_query.middleware.register(message_game_middleware)

async def message_game_middleware(
        handler: Callable[[CallbackQuery, Dict[str, Any]], Awaitable[Any]],
        callback: CallbackQuery,
        data: Dict[str, Any]
) -> Any:
    game = (await RandomChoiceGame.objects.aget(id=callback.data.split(":")[-1]))[0]
    data['game'] = game
    return await handler(callback, data)
