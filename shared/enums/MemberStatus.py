from enum import Enum


class MemberStatus(Enum):
    LEFT = "left"
    RESTRICTED = "restricted"
    MEMBER = "member"
    ADMIN = "admin"
    OWNER = "owner"
