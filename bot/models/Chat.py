from datetime import timedelta

from aiogram.enums.chat_type import ChatType
from django.db import models

from shared.utils import enum_to_choices


class Chat(models.Model):
    id = models.BigIntegerField(primary_key=True, null=False, editable=False, blank=False)
    name = models.TextField(null=False, blank=False)
    type = models.TextField(choices=enum_to_choices(ChatType), default=ChatType.PRIVATE.value, null=False, blank=False)
    users = models.ManyToManyField("User", through="ChatMember")

    updated_at = models.DateTimeField(auto_now=True)

    can_admins_join_games = models.BooleanField(default=True, null=False)
    can_admins_create_games = models.BooleanField(default=True, null=False)

    min_punish_time_for_rand_choice = models.DurationField(default=timedelta(minutes=1), null=False)
    max_punish_time_for_rand_choice = models.DurationField(default=timedelta(days=1), null=False)
    can_admins_ignore_time_limitations = models.BooleanField(default=False, null=False)
