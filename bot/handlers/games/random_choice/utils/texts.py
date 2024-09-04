from asgiref.sync import sync_to_async, async_to_sync
from django.utils.translation import gettext as _
from django.db.models import F

from games.models import RandomChoiceGame, RandomChoiceGameResult


@sync_to_async
def get_players(game: RandomChoiceGame) -> str:
    text = _("%(game_text)s\n\n"
             "Players:\n" % {"game_text": async_to_sync(game.get_string)()})

    player_index = 1
    for player in game.players.annotate(join_at=F('randomchoicegameplayer__join_at')).order_by("join_at"):
        text += f"{player_index}) {'👑 ' if player.id == game.creator_id else ''}{player.get_string(True)}\n"
        player_index += 1

    return text

@sync_to_async
def get_losers(game_result: RandomChoiceGameResult) -> str:
    text = ""
    for player in game_result.game.players.annotate(join_at=F('randomchoicegameplayer__join_at')).order_by("join_at"):
        if game_result.losers.filter(chat_member=player).exists():
            text += _("%(player)s ◀️\n" % {"player": player.get_string(True)})
        else:
            text += f"{player.get_string(True)}\n"

    return text
