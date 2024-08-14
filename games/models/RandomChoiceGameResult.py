from uuid import uuid4

from django.db import models

from games.models import RandomChoiceGame, RandomChoiceGamePlayer


class RandomChoiceGameResult(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid4, editable=False)
    game = models.ForeignKey(RandomChoiceGame, on_delete=models.CASCADE)
    losers = models.ManyToManyField(RandomChoiceGamePlayer)

    finished_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"[game {self.game}] - [finished at {self.finished_at}]"
