from django.db.models import Manager

from games.models.base_game_models import GameResultBase


class HiddenMinesGameResult(GameResultBase):
    game_name = "HiddenMines"

    winners: Manager

    def get_string(self):
        if self.losers.count() > 0:
            return _("""
            %(player)s, you lost.
            """) % {"player": self.losers.first().player}
        elif self.winners.count() > 0:
            return _("""
            %(player)s, you won.
            """) % {"player": self.winners.first().player}
