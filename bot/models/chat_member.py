from uuid import uuid4

from aiogram.enums.chat_type import ChatType
from aiogram.types import Chat as TeleChat, ChatMemberAdministrator, ChatMemberMember, ChatMemberOwner, ChatMemberRestricted, ChatMemberLeft
from django.conf import settings
from django.db import models

from shared.enums import MemberStatus
from shared.utils import enum_to_choices
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from bot.models import User


class ChatMember(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid4, editable=False)
    user = models.ForeignKey("User", on_delete=models.CASCADE, null=False, blank=False)
    chat = models.ForeignKey("Chat", on_delete=models.CASCADE, null=False, blank=False)

    status = models.TextField(choices=enum_to_choices(MemberStatus), default=MemberStatus.MEMBER.value, null=False)
    is_anon = models.BooleanField(default=False, null=False)
    can_interact = models.BooleanField(default=True, null=False)

    settings_group = models.ForeignKey("AccessGroup", on_delete=models.SET_NULL, null=True, default=None)

    updated_at = models.DateTimeField(auto_now=True)

    local_settings = models.ForeignKey("UserSettingsObject", on_delete=models.SET_NULL, null=True, blank=False, default=None)

    @property
    def settings(self):
        return self.local_settings if self.local_settings else self.user.global_settings

    def is_admin(self) -> bool:
        return self.is_owner() or self.status == MemberStatus.ADMIN.value

    def is_owner(self) -> bool:
        return self.is_super_admin() or self.status == MemberStatus.OWNER.value

    def is_super_admin(self) -> bool:
        return self.user_id in settings.ADMINS

    def get_string(self, with_link = False) -> str:
        status_mark = {MemberStatus.MEMBER.value: "",
                       MemberStatus.RESTRICTED.value: "",
                       MemberStatus.LEFT.value: "",
                       MemberStatus.ADMIN.value: "🅰️ ",
                       MemberStatus.OWNER.value: "🅾️ "}
        user_name = self.chat.name if self.is_anon else self.user.get_string(with_link)
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
