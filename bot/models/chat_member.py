from typing import TYPE_CHECKING
from uuid import uuid4

from aiogram.enums.chat_type import ChatType
from aiogram.types import Chat as TeleChat, ChatMemberAdministrator, ChatMemberMember, ChatMemberOwner, ChatMemberRestricted, ChatMemberLeft
from asgiref.sync import sync_to_async
from django.conf import settings
from django.db import models

from shared.enums import MemberStatus
from shared.utils import enum_to_choices

if TYPE_CHECKING:
    from bot.models import User


class ChatMember(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid4, editable=False)
    user = models.ForeignKey("User", on_delete=models.CASCADE, null=False, blank=False)
    chat = models.ForeignKey("Chat", on_delete=models.CASCADE, null=False, blank=False)

    status = models.TextField(choices=enum_to_choices(MemberStatus), default=MemberStatus.MEMBER.value, null=False)
    is_anon = models.BooleanField(default=False, null=False)
    can_interact = models.BooleanField(default=True, null=False)

    access_group = models.ForeignKey("AccessGroup", on_delete=models.SET_NULL, null=True, default=None)

    updated_at = models.DateTimeField(auto_now=True)

    local_settings = models.ForeignKey("UserSettingsObject", on_delete=models.SET_NULL, null=True, blank=False, default=None)

    @property
    def private_settings(self):
        return self.local_settings if self.local_settings else self.user.global_settings

    @property
    async def access_settings(self):
        from bot.models import AccessSettings, AccessSettingsObject
        from shared.enums import SettingsTarget

        target = None

        if self.is_super_admin():
            target = SettingsTarget.SUPER_ADMIN.value
        elif self.is_owner():
            target = SettingsTarget.OWNER.value

        if target:
            if await AccessSettings.objects.filter(chat__id=self.chat_id, target=target).aexists():
                _settings: AccessSettings = await AccessSettings.objects.filter(chat__id=self.chat_id, target=target).aget()
                return await sync_to_async(lambda: _settings.settings_object)()
            else:
                return await AccessSettingsObject.get_full_access_settings()

        filters = [
            (SettingsTarget.MEMBER.value, self.id),
            (SettingsTarget.GROUP.value, self.access_group_id),
            (SettingsTarget.ADMINS.value, self.chat_id),
            (SettingsTarget.CHAT.value, self.chat_id),
        ]

        for target, target_id in filters:
            if target == SettingsTarget.GROUP.value and self.access_group_id is None:
                continue
            if target == SettingsTarget.ADMINS.value and not self.is_admin():
                continue
            if await AccessSettings.objects.filter(chat__id=self.chat_id, target=target).aexists():
                access_settings: AccessSettings = await AccessSettings.objects.filter(chat__id=self.chat_id, target=target,
                                                                                      target_id=target_id).afirst()
                if access_settings:
                    return await sync_to_async(lambda: access_settings.settings_object)()
                else:
                    continue

        return None

    def is_admin(self) -> bool:
        return self.is_owner() or self.status == MemberStatus.ADMIN.value

    def is_owner(self) -> bool:
        return self.status == MemberStatus.OWNER.value

    def is_super_admin(self) -> bool:
        return self.user_id in settings.ADMINS

    def get_string(self, with_link=False) -> str:
        status_mark = {MemberStatus.MEMBER.value: "",
                       MemberStatus.RESTRICTED.value: "",
                       MemberStatus.LEFT.value: "",
                       MemberStatus.ADMIN.value: "🅰️ ",
                       MemberStatus.OWNER.value: "🅾️ "}
        user_name = self.chat.name if self.is_anon else self.user.get_string(with_link or self.private_settings.ping_in_stats)
        return f"{status_mark[self.status]}{user_name}"

    @staticmethod
    async def get_or_create_member(user: 'User', tele_chat: TeleChat):
        from bot.models import Chat
        chat = await Chat.objects.aget(id=tele_chat.id)
        member = (await ChatMember.objects.aget_or_create(user=user, chat=chat))[0]

        if chat.type != ChatType.PRIVATE:
            tele_member = await tele_chat.get_member(user.id)
            status = {ChatMemberLeft: MemberStatus.LEFT.value,
                      ChatMemberRestricted: MemberStatus.RESTRICTED.value,
                      ChatMemberMember: MemberStatus.MEMBER.value,
                      ChatMemberAdministrator: MemberStatus.ADMIN.value,
                      ChatMemberOwner: MemberStatus.OWNER.value}
            member.status = status[type(tele_member)]
        await member.asave()

        return member

    def __str__(self):
        return f"[id: {self.id}] - [status: {self.status}] - [can_interact: {self.can_interact}]"
