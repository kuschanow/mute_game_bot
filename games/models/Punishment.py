from datetime import timedelta
from uuid import uuid4

from django.core.exceptions import ValidationError
from django.db import models

from bot.models import Chat, User


class Punishment(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid4, editable=False)
    name = models.TextField(null=False, blank=False, default="untitled")
    time = models.DurationField(default=timedelta(hours=5))

    created_by = models.ForeignKey(User, null=True, on_delete=models.SET_NULL)
    created_in = models.ForeignKey(Chat, null=True, on_delete=models.SET_NULL)

    is_public = models.BooleanField(default=False, null=False)

    is_deleted = models.BooleanField(default=False, null=False)

    def get_string(self) -> str:
        # h = int(self.time.total_seconds() // 3600)
        # m = int(self.time.total_seconds() // 60 - h * 60)
        # return f"{self.name} ({h:02}:{m:02})"
        return f"{self.name} {str(self.time).replace(' days,', '')[:-3]}"

    def clean(self):
        cleaned_data = super().clean()
        created_in = cleaned_data.get("created_in")
        is_public = cleaned_data.get("is_public")

        if created_in is None and is_public:
            raise ValidationError(f"Punishment cannot be public if chat is not given")

    def __str__(self):
        return f"[name {self.name}] - [time {self.time}] - [public {self.is_public}]"
