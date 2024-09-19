from typing import Optional, Dict, Any, List, Tuple

from asgiref.sync import sync_to_async
from django.conf import settings

from bot.models import ChatMember, AccessSettingsObject
from games.models import Punishment


@sync_to_async
def get_punishments_keyboard(
        chat_member: ChatMember,
        member_settings: AccessSettingsObject,
        public_indicator: int,
        page: int,
        time_filters: Optional[Dict[str, Any]] = None
) -> List[List[str | Tuple[str, Dict[str, Any]]]]:
    start_index = page * settings.PAGE_SIZE
    end_index = (page + 1) * settings.PAGE_SIZE

    filters = {
        'is_deleted': False,
        'is_public': public_indicator == 1,
    }

    if public_indicator > -1:
        filters['created_in'] = chat_member.chat
    else:
        filters['created_in__isnull'] = True

    if public_indicator < 1:
        filters['created_by'] = chat_member.user

    if time_filters:
        filters.update(time_filters)

    filters = {k: v for k, v in filters.items() if v}

    query = Punishment.objects.filter(**filters).order_by("time")

    punishments = query[start_index:end_index]
    punishments_count = query.count()

    if len(punishments) == 0 and page > 0:
        raise Exception("Invalid page number")

    buttons = []
    for p in punishments:
        buttons.append([("punishment", {"id": str(p.id), "name": p.get_string()})])

    privacy = [
        ("privacy", {"public_indicator": -1}),
        ("privacy", {"public_indicator": 0})
    ]

    if member_settings.can_delete_public_punishments:
        privacy.append(("privacy", {"public_indicator": 1}))

    privacy.pop(public_indicator + 1)

    navigation = []

    if page > 0:
        navigation.append(("change_page", {"to_page": "prev", "page": page - 1}))
    if punishments_count - (page + 1) * settings.PAGE_SIZE > 0:
        navigation.append(("change_page", {"to_page": "next", "page": page + 1}))

    buttons.append(navigation)
    buttons.append(privacy)
    buttons.append(["cancel"])

    return buttons
