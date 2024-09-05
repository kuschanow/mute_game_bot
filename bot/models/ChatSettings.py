import uuid
from datetime import timedelta

from django.db import models



class ChatSettings(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    track_ban_statistic = models.BooleanField(default=False, null=False)