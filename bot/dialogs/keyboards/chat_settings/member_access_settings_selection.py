from typing import List

from aiogram_dialog_manager import Dialog
from aiogram_dialog_manager.instance import ButtonInstance
from asgiref.sync import sync_to_async
from django.conf import settings

from bot.dialogs.dialog_buttons import cancel, back, change_page, member_access_settings
from bot.models import ChatMember, AccessSettings
from shared.enums import SettingsTarget


def sync_get_member_access_settings_selection_keyboard(dialog: Dialog) -> List[List[ButtonInstance]]:
    page = dialog.values["page"]

    start_index = page * settings.PAGE_SIZE
    end_index = (page + 1) * settings.PAGE_SIZE

    access_settings_query = AccessSettings.objects.filter(target=SettingsTarget.MEMBER.value, chat_id=dialog.chat_id)
    query = sorted([ChatMember.objects.get(id=access_settings.target_id) for access_settings in access_settings_query],
                   key=lambda x: x.user.get_string())

    members = query[start_index:end_index]
    members_count = len(query)

    if len(members) == 0 and page > 0:
        dialog.data["page"] = (len(query) - 1) // settings.PAGE_SIZE
        return sync_get_member_access_settings_selection_keyboard(dialog)

    buttons = []

    for member in members:
        buttons.append([member_access_settings.get_instance({"id": str(member.id), "name": member.get_string()})])

    navigation = []

    if page > 0:
        navigation.append(change_page.get_instance({"to_page": "prev", "page": page - 1}))
    if members_count - (page + 1) * settings.PAGE_SIZE > 0:
        navigation.append(change_page.get_instance({"to_page": "next", "page": page + 1}))

    buttons.append(navigation)
    buttons.append([back.get_instance({"page": "target"})])
    buttons.append([cancel.get_instance()])

    return buttons


get_member_access_settings_selection_keyboard = sync_to_async(sync_get_member_access_settings_selection_keyboard)
