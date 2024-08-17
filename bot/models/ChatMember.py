from uuid import uuid4

from django.db import models

from bot.models import User, Chat


class ChatMember(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=False, blank=False)
    chat = models.ForeignKey(Chat, on_delete=models.CASCADE, null=False, blank=False)

    is_admin = models.BooleanField(default=False)
    can_interact_with_bot = models.BooleanField(default=True)

    updated_at = models.DateTimeField(auto_now=True)
