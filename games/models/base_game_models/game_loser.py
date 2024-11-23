from uuid import uuid4

from django.db import models


class GameLoserBase(models.Model):
    game_name = ""

    id = models.UUIDField(primary_key=True, default=uuid4, editable=False)
    game_result = None
    player = None

    def __init_subclass__(cls, **kwargs):
        super().__init_subclass__(**kwargs)
        if not cls.game_name:
            raise ValueError("You need to specify 'game_name' in the subclass.")

        cls.game_result = models.ForeignKey(f"{cls.game_name}GameResult", on_delete=models.CASCADE)  # type: ignore
        cls.player = models.ForeignKey(f"{cls.game_name}GamePlayer", on_delete=models.CASCADE)  # type: ignore

    def __str__(self):
        return f"[game {self.game_result}] - [player {self.player}]"

    class Meta:
        abstract = True
