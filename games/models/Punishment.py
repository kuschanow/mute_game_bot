from datetime import timedelta
from uuid import uuid4

from django.db import models

from bot.models import User
from shared.enums import AccessLevel
from shared.utils import enum_to_choices


class Punishment(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid4, editable=False)
    name = models.TextField(null=False, blank=False, unique=True)
    time = models.DurationField(default=timedelta(hours=5))

    created_by = models.ForeignKey(User, on_delete=User.get_sentinel)
    is_public = models.BooleanField(null=False, default=False)

    access_level = models.TextField(null=False, blank=False, choices=enum_to_choices(AccessLevel), default=AccessLevel.USER.value)

    @staticmethod
    def get_sentinel():
        return Punishment.objects.get_or_create(name="deleted")[0]

    def __str__(self):
        return f"[name {self.name}] - [time {self.time}] - [access {self.access_level}]"
