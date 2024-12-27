from uuid import uuid4

from asgiref.sync import sync_to_async
from django.db import models
from django.db.models import Manager, F
from django.utils.translation import gettext as _

from .game import GameBase


class GameResultMeta(models.base.ModelBase):
    def __new__(cls, name, bases, dct):
        new_class: GameResultBase = super().__new__(cls, name, bases, dct)  # type: ignore
        if not new_class._meta.abstract:  # Только для неабстрактных моделей
            if not hasattr(new_class, 'game_name') or not new_class.game_name:
                raise ValueError("You need to specify 'game_name' in the subclass.")

            new_class.add_to_class(
                "losers",
                models.ManyToManyField(
                    f"{new_class.game_name}GamePlayer",
                    through=f"{new_class.game_name}GameLoser"  # type: ignore
                )
            )

            new_class.add_to_class(
                "game",
                models.OneToOneField(
                    f"{new_class.game_name}Game",  # type: ignore
                    null=True,
                    default=None,
                    on_delete=models.CASCADE,
                    related_name="result"
                )
            )
        return new_class


class GameResultBase(models.Model, metaclass=GameResultMeta):
    game_name = ""

    id = models.UUIDField(primary_key=True, default=uuid4, editable=False)
    finished_at = models.DateTimeField(auto_now_add=True)

    game: GameBase
    losers: Manager

    @sync_to_async
    def get_losers(self) -> str:
        text = ""
        for player in self.game.players.annotate(join_at=F(f'{self.game_name.lower()}gameplayer__join_at')).order_by("join_at"):
            if self.losers.filter(chat_member=player).exists():
                text += _("▶ %(player)s\n") % {"player": player.get_string(True)}
            else:
                text += f"{player.get_string(True)}\n"

        return text

    def __str__(self):
        return f"[game {self.game}] - [finished at {self.finished_at}]"

    class Meta:
        abstract = True
