import uuid
from datetime import timedelta
from typing import Dict

from django.db import models


class UserSettingsObject(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    ping_in_stats = models.BooleanField(default=False, null=False)
