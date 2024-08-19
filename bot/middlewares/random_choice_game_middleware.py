from typing import Callable, Dict, Any, Awaitable

from aiogram import Router
from aiogram.types import CallbackQuery
from asgiref.sync import sync_to_async

from games.models import RandomChoiceGame


def set_random_choice_game_middlewares(router: Router):
    router.callback_query.outer_middleware.register(message_game_middleware)

async def message_game_middleware(
        handler: Callable[[CallbackQuery, Dict[str, Any]], Awaitable[Any]],
        callback: CallbackQuery,
        data: Dict[str, Any]
) -> Any:
    query = await sync_to_async(lambda: RandomChoiceGame.objects.filter(id=callback.data.split(":")[-1]))()
    if await sync_to_async(lambda: query.exists())():
        game = (await RandomChoiceGame.objects.aget(id=callback.data.split(":")[-1]))
    else:
        game = None
    data['game'] = game
    return await handler(callback, data)
