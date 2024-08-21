from uuid import uuid4

from django.db import models

from shared.enums import MemberStatus, InteractionLevel
from shared.utils import enum_to_choices


class ChatMember(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid4, editable=False)
    user = models.ForeignKey("User", on_delete=models.CASCADE, null=False, blank=False)
    chat = models.ForeignKey("Chat", on_delete=models.CASCADE, null=False, blank=False)

    status = models.TextField(choices=enum_to_choices(MemberStatus), default=MemberStatus.MEMBER.value, null=False)
    is_anon = models.BooleanField(default=False, null=False)
    interaction_level = models.TextField(choices=enum_to_choices(InteractionLevel), default=InteractionLevel.BASED_ON_STATUS.value, null=False)


    updated_at = models.DateTimeField(auto_now=True)

    def get_string(self, with_link = False) -> str:
        status_mark = {MemberStatus.MEMBER.value: "",
                       MemberStatus.ADMIN.value: "🅰️ ",
                       MemberStatus.OWNER.value: "🅾️ "}
        user_name = self.chat.name if self.is_anon else self.user.get_string(with_link)
        return f"{status_mark[self.status]}{user_name}"
