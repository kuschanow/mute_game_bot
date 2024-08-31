from aiogram.enums.chat_type import ChatType
from aiogram.types import Chat as TeleChat
from asgiref.sync import sync_to_async
from django.db import models

from bot.models.AccessSettings import AccessSettings
from shared.enums import SettingsTarget
from shared.utils import enum_to_choices


class Chat(models.Model):
    id = models.BigIntegerField(primary_key=True, null=False, editable=False, blank=False)
    name = models.TextField(null=False, blank=False)
    type = models.TextField(choices=enum_to_choices(ChatType), default=ChatType.PRIVATE.value, null=False, blank=False)
    users = models.ManyToManyField("User", through="ChatMember")

    updated_at = models.DateTimeField(auto_now=True)

    @staticmethod
    async def get_or_create_chat(tele_chat: TeleChat):
        chat, created = await Chat.objects.aget_or_create(id=tele_chat.id)

        chat.name = tele_chat.full_name
        chat.type = tele_chat.type
        await chat.asave()

        if created:
            from bot.models import AccessSettingsObject

            settings_object = AccessSettingsObject()
            await settings_object.asave()

            await AccessSettings.objects.acreate(
                chat=chat,
                target=SettingsTarget.CHAT.value,
                target_id=chat.id,
                settings_object=settings_object
            )

        return chat