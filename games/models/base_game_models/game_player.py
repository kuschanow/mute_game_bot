from uuid import uuid4

from django.db import models

from bot.models import ChatMember


class GamePlayerBase(models.Model):
    game_name = ""

    id = models.UUIDField(primary_key=True, default=uuid4, editable=False)
    game = None
    chat_member = models.ForeignKey(ChatMember, on_delete=models.CASCADE)
    join_at = models.DateTimeField(auto_now_add=True)

    def __init_subclass__(cls, **kwargs):
        super().__init_subclass__(**kwargs)
        if not cls.game_name:
            raise ValueError("You need to specify 'game_name' in the subclass.")

        cls.game = models.ForeignKey(f"{cls.game_name}Game", on_delete=models.CASCADE)  # type: ignore

    def __str__(self):
        return f"[game {self.game}] - [chat member {self.chat_member}]"

    class Meta:
        abstract = True
