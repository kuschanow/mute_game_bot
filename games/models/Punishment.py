from datetime import timedelta
from uuid import uuid4

from django.db import models

from bot.models import ChatMember


class Punishment(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid4, editable=False)
    name = models.TextField(null=False, blank=False, default="untitled")
    time = models.DurationField(default=timedelta(hours=5))

    created_by = models.ForeignKey(ChatMember, on_delete=models.SET_NULL)

    is_public = models.BooleanField(default=False, null=False)

    is_deleted = models.BooleanField(default=False, null=False)

    def __str__(self):
        return f"[name {self.name}] - [time {self.time}] - [public {self.is_public}]"
