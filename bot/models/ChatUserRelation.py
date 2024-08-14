from django.db import models

from bot.models import User, Chat


class CharUserRelation(models.Model):
    user = models.ForeignKey(User, on_delete=User.get_sentinel, null=False, blank=False)
    chat = models.ForeignKey(Chat, on_delete=Chat.get_sentinel, null=False, blank=False)
    updated_at = models.DateTimeField(auto_now=True)
