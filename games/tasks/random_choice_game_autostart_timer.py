from asgiref.sync import async_to_sync
from celery import shared_task


@shared_task(serializer='pickle')
def random_choice_game_autostart_timer(game_id: str, chat_id: int):
    from games.models import RandomChoiceGame
    from bot.models import Chat
    from bot.handlers.games.utils import mute_losers

    game = RandomChoiceGame.objects.get(id=game_id)
    chat = Chat.objects.get(id=chat_id)

    if game.result:
        return

    if game.autostart_at:
        return

    players_count = game.players.count()
    autostart_at_max_players_condition = (not game.autostart_at_max_players or
                                          (game.autostart_at_max_players and players_count == game.max_players_count))
    operator = game.autostart_operator

    if (operator == "or" and players_count >= game.min_players_count) or \
            (operator != "or" and autostart_at_max_players_condition):
        result = async_to_sync(game.start_game)()
        mute_losers(game, result, chat)
