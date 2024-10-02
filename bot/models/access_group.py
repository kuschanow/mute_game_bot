from uuid import uuid4

from django.db import models


class AccessGroup(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid4, editable=False)
    chat = models.ForeignKey("Chat", on_delete=models.CASCADE, null=False, blank=False)
    name = models.TextField(null=False, blank=False, default="untitled group")

    created_at = models.DateTimeField(auto_now_add=True)
