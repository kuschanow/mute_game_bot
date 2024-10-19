from typing import List

from aiogram_dialog_manager import Dialog
from aiogram_dialog_manager.instance import ButtonInstance
from asgiref.sync import sync_to_async
from django.conf import settings

from bot.dialogs.dialog_buttons import cancel, back, change_page, access_group, add
from bot.models import AccessGroup


def sync_get_access_group_selection_keyboard(dialog: Dialog, creating: bool = False) -> List[List[ButtonInstance]]:
    page = dialog.values["page"]

    start_index = page * settings.PAGE_SIZE
    end_index = (page + 1) * settings.PAGE_SIZE

    query = AccessGroup.objects.filter().order_by("created_at")

    groups = query[start_index:end_index]
    groups_count = query.count()

    if len(groups) == 0 and page > 0:
        dialog.data["page"] = (query.count() - 1) // settings.PAGE_SIZE
        return sync_get_access_group_selection_keyboard(dialog)

    buttons = []

    for group in groups:
        buttons.append([access_group.get_instance({"id": str(group.id), "name": group.name})])

    navigation = []

    if page > 0:
        navigation.append(change_page.get_instance({"to_page": "prev", "page": page - 1}))
    if groups_count - (page + 1) * settings.PAGE_SIZE > 0:
        navigation.append(change_page.get_instance({"to_page": "next", "page": page + 1}))

    buttons.append(navigation)
    buttons.append([add.get_instance({"state": "selected"} if creating else {})])
    buttons.append([back.get_instance({"page": "target"})])
    buttons.append([cancel.get_instance()])

    return buttons


get_access_group_selection_keyboard = sync_to_async(sync_get_access_group_selection_keyboard)
