from typing import Optional, List

from aiogram_dialog_manager import Dialog
from aiogram_dialog_manager.instance import ButtonInstance
from bot.utils.dialog.dialog_buttons import ping_in_stats, cancel, make_diff, reset_to_global

from bot.models import UserSettingsObject


def get_user_settings(dialog: Dialog, settings_object: Optional[UserSettingsObject]) -> List[List[ButtonInstance]]:
    if settings_object:
        buttons = [
            [ping_in_stats.get_instance({"status": '✅' if settings_object.ping_in_stats else '☑️'})]
        ]

        if dialog.values["settings_type"] == "local":
            buttons.append([reset_to_global.get_instance()])
    else:
        buttons = [
            [make_diff.get_instance()]
        ]

    buttons.append([cancel.get_instance()])

    return buttons

