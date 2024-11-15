import asyncio

from celery import shared_task


@shared_task
def random_choice_game_autostart_timer(game_id: str, chat_id: int, dialog_id: str):
    from games.models import RandomChoiceGame
    from bot.models import Chat

    game = RandomChoiceGame.objects.get(id=game_id)
    chat = Chat.objects.get(id=chat_id)

    if game.is_finished():
        return

    players_count = game.players.count()
    autostart_at_max_players_condition = (not game.autostart_at_max_players or
                                          (game.autostart_at_max_players and players_count == game.max_players_count))
    operator = game.autostart_operator

    if (operator == "or" and players_count >= game.min_players_count) or \
            (operator != "or" and autostart_at_max_players_condition):
        asyncio.run(asyncio.wait_for(mute(chat, game, dialog_id), timeout=None))


async def mute(chat, game, dialog_id):
    from bot.handlers.games.utils import mute_losers
    from bot.handlers.games.random_choice import random_choice_game_dialog_manager
    from bot.dialogs.dialog_texts import random_choice_game_texts
    from bot.handlers.games.random_choice.utils.texts import get_losers

    result = await game.start_game()
    await mute_losers(game, result, chat)

    dialog = await random_choice_game_dialog_manager.get_dialog(dialog_id)

    await dialog.edit_message(dialog.values["main_message_id"], random_choice_game_texts["game"])
    dialog.data["game_losers"] = await get_losers(result)
    dialog.data["game_text"] = await game.get_string()
    await dialog.send_message(random_choice_game_texts["results"], reply_to_message_id=dialog.values["main_message_id"])
    await random_choice_game_dialog_manager.delete_dialog(dialog)
