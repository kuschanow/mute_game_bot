import re
from uuid import uuid4

from django.db import models
from django.db.models import Manager

from bot.models import ChatMember


class GameMeta(models.base.ModelBase):
    def __new__(cls, name, bases, dct):
        new_class: GameBase = super().__new__(cls, name, bases, dct)  # type: ignore
        if not new_class._meta.abstract:
            if not hasattr(new_class, 'game_name') or not new_class.game_name:
                raise ValueError("You need to specify 'game_name' in the subclass.")

            def camel_to_snake(name):
                return re.sub('([a-z0-9])([A-Z])', r'\1_\2', name).lower()

            new_class.add_to_class(
                "creator",
                models.ForeignKey(
                    ChatMember,
                    null=True,
                    blank=False,
                    on_delete=models.SET_NULL,
                    related_name=f"created_{camel_to_snake(new_class.game_name)}_games"
                )
            )

            new_class.add_to_class(
                "players",
                models.ManyToManyField(
                    ChatMember,
                    through=f"{new_class.game_name}GamePlayer",
                    related_name=f"participated_{camel_to_snake(new_class.game_name)}_games"
                )
            )
        return new_class


class GameBase(models.Model, metaclass=GameMeta):
    game_name = ""

    id = models.UUIDField(primary_key=True, default=uuid4, editable=False)
    punishment = models.ForeignKey("Punishment", on_delete=models.CASCADE)
    is_creator_playing = models.BooleanField(default=True)
    is_opened_to_join = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    creator: ChatMember
    players: Manager

    @property
    def is_finished(self):
        return hasattr(self, "result")

    def __str__(self):
        return f"[id {self.id}] - [creator {self.creator}] - [punishment {self.punishment}]"

    class Meta:
        abstract = True
