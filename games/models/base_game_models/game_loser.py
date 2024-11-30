from uuid import uuid4

from django.db import models

from .game_player import GamePlayerBase
from .game_result import GameResultBase


class GameLoserMeta(models.base.ModelBase):
    def __new__(cls, name, bases, dct):
        new_class: GameLoserBase = super().__new__(cls, name, bases, dct)  # type: ignore
        if not new_class._meta.abstract:
            if not hasattr(new_class, 'game_name') or not new_class.game_name:
                raise ValueError("You need to specify 'game_name' in the subclass.")

            # Добавляем ForeignKey для game_result и player
            new_class.add_to_class(
                "game_result",
                models.ForeignKey(
                    f"{new_class.game_name}GameResult",
                    on_delete=models.CASCADE
                )
            )
            new_class.add_to_class(
                "player",
                models.ForeignKey(
                    f"{new_class.game_name}GamePlayer",
                    on_delete=models.CASCADE
                )
            )
        return new_class


class GameLoserBase(models.Model, metaclass=GameLoserMeta):
    game_name = ""

    id = models.UUIDField(primary_key=True, default=uuid4, editable=False)

    game_result: GameResultBase
    player: GamePlayerBase

    def __str__(self):
        return f"[game {self.game_result}] - [player {self.player}]"

    class Meta:
        abstract = True
