from uuid import uuid4

from django.db import models

from bot.models import ChatMember


class RandomChoiceGamePlayer(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid4, editable=False)
    game = models.ForeignKey("RandomChoiceGame", on_delete=models.CASCADE)
    chat_member = models.ForeignKey(ChatMember, on_delete=models.CASCADE)
    join_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"[game {self.game}] - [chat member {self.chat_member}]"

