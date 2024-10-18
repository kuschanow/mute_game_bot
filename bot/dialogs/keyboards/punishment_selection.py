from typing import Optional, Dict, Any, List, Tuple

from aiogram_dialog_manager import Dialog
from asgiref.sync import sync_to_async, async_to_sync
from django.conf import settings

from bot.dialogs.dialog_buttons import cancel, privacy, punishment, change_page
from bot.models import ChatMember
from games.models import Punishment


def sync_get_punishments_keyboard(
        dialog: Dialog,
        chat_member: ChatMember,
        time_filters: Optional[Dict[str, Any]] = None
) -> List[List[str | Tuple[str, Dict[str, Any]]]]:
    page = dialog.values["page"]
    public_indicator = dialog.values["public_indicator"]

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
        dialog.data["page"] = (query.count() - 1) // settings.PAGE_SIZE
        return sync_get_punishments_keyboard(dialog, chat_member, time_filters)

    buttons = []
    for p in punishments:
        buttons.append([punishment.get_instance({"id": str(p.id), "name": p.get_string()})])

    privacy_block = [
        privacy.get_instance({"public_indicator": -1}),
        privacy.get_instance({"public_indicator": 0}),
        privacy.get_instance({"public_indicator": 1})
    ]

    if dialog.name == "punishment_deletion" and not async_to_sync(lambda: chat_member.access_settings)().can_delete_public_punishments:
        privacy_block.pop(2)

    privacy_block.pop(public_indicator + 1)

    navigation = []

    if page > 0:
        navigation.append(change_page.get_instance({"to_page": "prev", "page": page - 1}))
    if punishments_count - (page + 1) * settings.PAGE_SIZE > 0:
        navigation.append(change_page.get_instance({"to_page": "next", "page": page + 1}))

    buttons.append(navigation)
    buttons.append(privacy_block)
    buttons.append([cancel.get_instance()])

    return buttons


get_punishments_keyboard = sync_to_async(sync_get_punishments_keyboard)
