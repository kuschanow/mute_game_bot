from django.db import models

from bot.models import User
from games.models import RandomChoiceGame


class RandomChoiceGamePlayer(models.Model):
    game = models.ForeignKey(RandomChoiceGame, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=User.get_sentinel)
    join_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"[game {self.game}] - [user {self.user}]"
