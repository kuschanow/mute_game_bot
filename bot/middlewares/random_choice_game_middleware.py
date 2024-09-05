from typing import Callable, Dict, Any, Awaitable

from aiogram import Router
from aiogram.types import CallbackQuery, Message
from asgiref.sync import sync_to_async, async_to_sync

from games.models import RandomChoiceGame


def set_random_choice_game_middlewares(router: Router):
    router.callback_query.outer_middleware.register(callback_game_middleware)
    router.message.outer_middleware.register(message_game_middleware)

async def callback_game_middleware(
        handler: Callable[[CallbackQuery, Dict[str, Any]], Awaitable[Any]],
        callback: CallbackQuery,
        data: Dict[str, Any]
) -> Any:
    if "rcg:" in callback.data or "rcgs:" in callback.data:
        query = await sync_to_async(lambda: RandomChoiceGame.objects.filter(id=callback.data.split(":")[-1]))()
        if await sync_to_async(lambda: query.exists())():
            game = (await RandomChoiceGame.objects.aget(id=callback.data.split(":")[-1]))
        else:
            game = None
        data['game'] = game
    return await handler(callback, data)

async def message_game_middleware(
        handler: Callable[[Message, Dict[str, Any]], Awaitable[Any]],
        callback: Message,
        data: Dict[str, Any]
) -> Any:
    if "game_id" in await data["state"].get_data():
        game_id = (await data["state"].get_data())["game_id"]
        query = await sync_to_async(lambda: RandomChoiceGame.objects.filter(id=game_id))()
        if await sync_to_async(lambda: query.exists())():
            game = (await RandomChoiceGame.objects.aget(id=game_id))
        else:
            game = None
        data['game'] = game
    return await handler(callback, data)
