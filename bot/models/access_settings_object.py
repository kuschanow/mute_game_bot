import uuid
from datetime import timedelta
from typing import Dict

from asgiref.sync import async_to_sync
from django.db import models


class AccessSettingsObject(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    can_join_games = models.BooleanField(default=True, null=False)
    can_create_games = models.BooleanField(default=True, null=False)
    can_press_other_buttons = models.BooleanField(default=False, null=False)

    min_punish_time_for_rand_choice = models.DurationField(default=timedelta(minutes=1), null=False)
    max_punish_time_for_rand_choice = models.DurationField(default=timedelta(days=365), null=True)

    can_create_public_punishments = models.BooleanField(default=False, null=False)
    can_delete_public_punishments = models.BooleanField(default=False, null=False)

    is_invulnerable = models.BooleanField(default=False, null=False)
    show_in_stats = models.BooleanField(default=True, null=False)

    @property
    def time_filters(self) -> Dict[str, timedelta]:
        return {"time__lte": self.max_punish_time_for_rand_choice,
                "time__gte": self.min_punish_time_for_rand_choice}

    @staticmethod
    async def get_full_access_settings():
        return (await AccessSettingsObject.objects.aget_or_create(
            id=uuid.UUID(int=0, version=4),

            can_join_games=True,
            can_create_games=True,
            can_press_other_buttons=True,

            min_punish_time_for_rand_choice=timedelta(minutes=1),
            max_punish_time_for_rand_choice=None,

            can_create_public_punishments=True,
            can_delete_public_punishments=True,

            is_invulnerable=True,
            show_in_stats=True,
        ))[0]

    def __str__(self):
        return (
            f"[can_join_games: {self.can_join_games}] - "
            f"[can_create_games: {self.can_create_games}] - "
            f"[can_press_other_buttons: {self.can_press_other_buttons}] - "
            f"[min_punish_time_for_rand_choice: {self.min_punish_time_for_rand_choice}] - "
            f"[max_punish_time_for_rand_choice: {self.max_punish_time_for_rand_choice}] - "
            f"[can_create_public_punishments: {self.can_create_public_punishments}] - "
            f"[can_delete_public_punishments: {self.can_delete_public_punishments}] - "
            f"[is_invulnerable: {self.is_invulnerable}] - "
            f"[show_in_stats: {self.show_in_stats}]")
