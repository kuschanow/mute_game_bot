from enum import Enum


class InteractionLevel(Enum):
    RESTRICTED = "restricted"
    BASED_ON_STATUS = "based_on_status"
    CAN_ADMINISTRATE = "can_administrate"
