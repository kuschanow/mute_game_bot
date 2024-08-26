import uuid
from datetime import timedelta

from django.db import models



class AccessSettingsObject(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    can_join_games = models.BooleanField(default=True, null=False)
    can_create_games = models.BooleanField(default=True, null=False)
    can_press_other_buttons = models.BooleanField(default=False, null=False)

    min_punish_time_for_rand_choice = models.DurationField(default=timedelta(minutes=1), null=False)
    max_punish_time_for_rand_choice = models.DurationField(default=None, null=True)

    can_create_public_punishments = models.BooleanField(default=False, null=False)
    can_delete_public_punishments = models.BooleanField(default=False, null=False)

    @staticmethod
    async def get_owner_settings():
        return (await AccessSettingsObject.objects.aget_or_create(
            id=uuid.UUID(int=0, version=4),

            can_join_games=True,
            can_create_games=True,
            can_press_other_buttons=True,

            min_punish_time_for_rand_choice=timedelta(minutes=1),
            max_punish_time_for_rand_choice=None,

            can_create_public_punishments=True,
            can_delete_public_punishments=True,
        ))[0]
