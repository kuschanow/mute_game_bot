from uuid import uuid4

from django.db import models

from bot.models.SettingsObject import SettingsObject
from shared.enums import SettingsTarget
from shared.utils import enum_to_choices


class ChatSettings(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid4, editable=False)

    chat = models.ForeignKey("Chat", on_delete=models.CASCADE, null=False)
    settings_object = models.ForeignKey("SettingsObject", on_delete=models.CASCADE, null=False)
    target = models.TextField(choices=enum_to_choices(SettingsTarget), default=SettingsTarget.CHAT.value, null=False, blank=False)
    target_id = models.TextField(null=False, blank=False)
