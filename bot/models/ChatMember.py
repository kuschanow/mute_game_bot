from uuid import uuid4

from aiogram.enums.chat_type import ChatType
from aiogram.types import Chat as TeleChat, ChatMemberAdministrator, ChatMemberMember, ChatMemberOwner, ChatMemberRestricted, ChatMemberLeft
from asgiref.sync import async_to_sync, sync_to_async
from django.conf import settings
from django.db import models

from bot.models import User
from shared.enums import InteractionLevel
from shared.enums import MemberStatus
from shared.utils import enum_to_choices


class ChatMember(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid4, editable=False)
    user = models.ForeignKey("User", on_delete=models.CASCADE, null=False, blank=False)
    chat = models.ForeignKey("Chat", on_delete=models.CASCADE, null=False, blank=False)

    status = models.TextField(choices=enum_to_choices(MemberStatus), default=MemberStatus.MEMBER.value, null=False)
    is_anon = models.BooleanField(default=False, null=False)
    interaction_level = models.TextField(choices=enum_to_choices(InteractionLevel), default=InteractionLevel.BASED_ON_STATUS.value, null=False)

    settings_group = models.ForeignKey("AccessGroup", on_delete=models.SET_NULL, null=True, default=None)

    updated_at = models.DateTimeField(auto_now=True)

    def is_admin(self) -> bool:
        return (self.user_id in settings.ADMINS or
                self.status == MemberStatus.ADMIN.value or
                self.status == MemberStatus.OWNER.value or
                self.interaction_level ==InteractionLevel.CAN_ADMINISTRATE.value)

    def is_owner(self) -> bool:
        return self.user_id in settings.ADMINS or self.status == MemberStatus.OWNER.value

    def is_super_admin(self) -> bool:
        return self.user_id in settings.ADMINS

    def get_string(self, with_link = False) -> str:
        status_mark = {MemberStatus.MEMBER.value: "",
                       MemberStatus.ADMIN.value: "🅰️ ",
                       MemberStatus.OWNER.value: "🅾️ "}
        user_name = self.chat.name if self.is_anon else self.user.get_string(with_link)
        return f"{status_mark[self.status]}{user_name}"

    @staticmethod
    async def get_or_create_member(user: User, tele_chat: TeleChat):
        from bot.models import Chat
        chat = await Chat.get_or_create_chat(tele_chat)
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
