from typing import List, Optional

from aiogram_dialog_manager import Dialog
from aiogram_dialog_manager.instance import ButtonInstance

from bot.models import AccessSettingsObject
from bot.dialogs.dialog_buttons import make_diff, back, can_join_games, can_create_games, can_press_other_buttons, can_create_punishments, \
    can_delete_punishments, games_settings, reset_to_global, is_invulnerable, show_in_stats, cancel


def get_access_settings_keyboard(dialog: Dialog, settings_object: Optional[AccessSettingsObject]) -> List[List[ButtonInstance]]:
    if settings_object is None:
        buttons = [
            [make_diff.get_instance()],
        ]
    else:
        buttons = [
            [can_join_games.get_instance({"status": '✅' if settings_object.can_join_games else '☑️'})],
            [can_create_games.get_instance({"status": '✅' if settings_object.can_create_games else '☑️'})],
            [can_press_other_buttons.get_instance({"status": '✅' if settings_object.can_press_other_buttons else '☑️'})],
            [can_create_punishments.get_instance({"status": '✅' if settings_object.can_create_public_punishments else '☑️'})],
            [can_delete_punishments.get_instance({"status": '✅' if settings_object.can_delete_public_punishments else '☑️'})],
            [is_invulnerable.get_instance({"status": '✅' if settings_object.is_invulnerable else '☑️'})],
            [show_in_stats.get_instance({"status": '✅' if settings_object.show_in_stats else '☑️'})],
            [games_settings.get_instance()],
        ]

        if dialog.values["target"] != "chat":
            buttons.append([reset_to_global.get_instance()])

    buttons.append([back.get_instance({"page": "target"})])
    buttons.append([cancel.get_instance()])

    return buttons
