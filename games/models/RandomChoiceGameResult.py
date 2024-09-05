from uuid import uuid4

from django.db import models


class RandomChoiceGameResult(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid4, editable=False)
    losers = models.ManyToManyField("RandomChoiceGamePlayer", through="RandomChoiceGameLoser")

    finished_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"[game {self.game}] - [finished at {self.finished_at}]"
