from enum import Enum


class SettingsTarget(Enum):
    SUPER_ADMIN = "super_admin"
    OWNER = "owner"
    CHAT = "chat"
    ADMINS = "admins"
    GROUP = "group"
    MEMBER = "member"
