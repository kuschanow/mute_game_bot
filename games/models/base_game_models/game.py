import re
from uuid import uuid4

from asgiref.sync import sync_to_async
from django.db import models

from bot.models import ChatMember


class GameBase(models.Model):
    game_name = ""

    id = models.UUIDField(primary_key=True, default=uuid4, editable=False)
    punishment = models.ForeignKey("Punishment", on_delete=models.CASCADE)

    creator = None
    players = None
    is_creator_playing = models.BooleanField(default=True, null=False)

    is_opened_to_join = models.BooleanField(null=False, default=False)

    created_at = models.DateTimeField(auto_now_add=True)

    def __init_subclass__(cls, **kwargs):
        super().__init_subclass__()
        if not cls.game_name:
            raise ValueError("You need to specify 'game_name' in the subclass.")

        def camel_to_snake(name):
            snake = re.sub('([a-z0-9])([A-Z])', r'\1_\2', name).lower()
            return snake

        cls.creator = models.ForeignKey(
            ChatMember,
            null=True,
            blank=False,
            on_delete=models.SET_NULL,
            related_name=f"created_{camel_to_snake(cls.game_name)}_games"
        )

        cls.players = models.ManyToManyField(
            ChatMember,
            through=f"{cls.game_name}GamePlayer",  # type: ignore
            related_name=f"participated_{camel_to_snake(cls.game_name)}_games"
        )

    @sync_to_async
    def is_finished(self) -> bool:
        self.is_finished = hasattr(self, "result")
        return self.is_finished

    def __str__(self):
        return f"[id {self.id}] - [creator {self.creator}] - [punishment {self.punishment}]"

    class Meta:
        abstract = True
