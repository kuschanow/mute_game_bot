from uuid import uuid4

from django.db import models


class GameResultBase(models.Model):
    game_name = ""

    id = models.UUIDField(primary_key=True, default=uuid4, editable=False)

    losers = None

    finished_at = models.DateTimeField(auto_now_add=True)

    game = None

    def __init_subclass__(cls, **kwargs):
        super().__init_subclass__(**kwargs)
        if not cls.game_name:
            raise ValueError("You need to specify 'game_name' in the subclass.")

        cls.losers = models.ManyToManyField(f"{cls.game_name}GamePlayer", through=f"{cls.game_name}GameLoser")  # type: ignore
        cls.game = models.OneToOneField(
            f"{cls.game_name}Game",  # type: ignore
            null=True, default=None,
            on_delete=models.CASCADE,
            related_name="result"
        )

    def __str__(self):
        return f"[game {self.game}] - [finished at {self.finished_at}]"

    class Meta:
        abstract = True
