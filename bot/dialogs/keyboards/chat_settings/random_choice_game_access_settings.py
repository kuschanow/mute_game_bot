from typing import List

from aiogram_dialog_manager.instance import ButtonInstance

from bot.dialogs.dialog_buttons import access_time_settings, back
from bot.models import AccessSettingsObject
from shared.utils import format_time


def get_random_choice_game_access_settings_keyboard(settings_object: AccessSettingsObject, highlight_this: str = "") -> List[List[ButtonInstance]]:
    min_time_data = {"time": format_time(settings_object.min_punish_time_for_rand_choice), "type": "min_time",
                     "selected": highlight_this == "min_time"}
    max_time_data = {"time": format_time(settings_object.max_punish_time_for_rand_choice), "type": "max_time",
                     "selected": highlight_this == "max_time"}

    buttons = [
        [access_time_settings.get_instance(min_time_data)],
        [access_time_settings.get_instance(max_time_data)],
        [back.get_instance({"page": "game_menu"})]
    ]

    return buttons
