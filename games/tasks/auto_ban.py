import asyncio
from typing import TYPE_CHECKING

from celery import shared_task

if TYPE_CHECKING:
    from bot.models import Chat
    from games.models import HiddenMinesGame


@shared_task
def auto_ban(game_id: str, chat_id: int, dialog_id: str):
    from bot.models import Chat

    game = HiddenMinesGame.objects.get(id=game_id)
    chat = Chat.objects.get(id=chat_id)

    if game.is_finished():
        return

    asyncio.run(game.finish_game_by_timeout())

    asyncio.run(mute(chat, game, dialog_id))


async def mute(chat: 'Chat', game: 'HiddenMinesGame', dialog_id: str):
    from bot.handlers.games.utils import mute_losers
    from bot.handlers.games.hidden_mines import hidden_mines_game_dialog_manager
    from bot.dialogs.dialog_texts import hidden_mines_game_texts

    await mute_losers(game, chat)

    dialog = await hidden_mines_game_dialog_manager.get_dialog(dialog_id)

    await dialog.edit_message(dialog.values["main_message_id"], hidden_mines_game_texts["results"])
    dialog.data["game_result"] = await game.result.get_string()  # type: ignore
    await hidden_mines_game_dialog_manager.delete_dialog(dialog)
