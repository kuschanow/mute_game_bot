from uuid import uuid4

from django.db import models


class RandomChoiceGameLoser(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid4, editable=False)
    game_result = models.ForeignKey("RandomChoiceGameResult", on_delete=models.CASCADE)
    player = models.ForeignKey("RandomChoiceGamePlayer", on_delete=models.CASCADE)

    def __str__(self):
        return f"[game {self.game_result}] - [player {self.player}]"
