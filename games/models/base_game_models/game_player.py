from uuid import uuid4

from django.db import models

from bot.models import ChatMember
from .game import GameBase


class GamePlayerMeta(models.base.ModelBase):
    def __new__(cls, name, bases, dct):
        new_class: GamePlayerBase = super().__new__(cls, name, bases, dct)  # type: ignore
        if not new_class._meta.abstract:
            if not hasattr(new_class, 'game_name') or not new_class.game_name:
                raise ValueError("You need to specify 'game_name' in the subclass.")

            new_class.add_to_class(
                "game",
                models.ForeignKey(
                    f"{new_class.game_name}Game",
                    on_delete=models.CASCADE
                )
            )
        return new_class


class GamePlayerBase(models.Model, metaclass=GamePlayerMeta):
    game_name = ""

    id = models.UUIDField(primary_key=True, default=uuid4, editable=False)
    chat_member = models.ForeignKey(ChatMember, on_delete=models.CASCADE)
    join_at = models.DateTimeField(auto_now_add=True)

    game: GameBase

    def __str__(self):
        return f"[game {self.game}] - [chat member {self.chat_member}]"

    class Meta:
        abstract = True
