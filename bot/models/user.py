from aiogram.types import User as TeleUser
from django.db import models


class User(models.Model):
    id = models.BigIntegerField(primary_key=True, null=False, editable=False, blank=False)
    username = models.TextField(null=True)
    first_name = models.TextField(null=False, blank=False)
    last_name = models.TextField(null=True)

    updated_at = models.DateTimeField(auto_now=True)

    global_settings = models.ForeignKey("UserSettingsObject", on_delete=models.CASCADE, null=False, blank=False)

    def get_string(self, with_link: bool = False):
       return f"<a href='tg://user?id={self.id}'>{self.first_name}{f' {self.last_name}' if self.last_name is not None else ''}</a>" if with_link \
           else f"{self.first_name}{f' {self.last_name}' if self.last_name is not None else ''}"

    @staticmethod
    async def get_or_create_user(tele_user: TeleUser):
        user, created = await User.objects.aget_or_create(id=tele_user.id)

        user.username = tele_user.username
        user.first_name = tele_user.first_name
        user.last_name = tele_user.last_name

        if created:
            from bot.models import UserSettingsObject
            user.global_settings = await UserSettingsObject.objects.acreate()

        await user.asave()

        return user

    def __str__(self):
        return f"[id: {self.id}] - [username: @{self.username}] - [name: {self.first_name}{f' {self.last_name}' if self.last_name is not None else ''}]"
