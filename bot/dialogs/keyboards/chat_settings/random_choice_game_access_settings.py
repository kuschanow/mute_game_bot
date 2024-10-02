from typing import List

from aiogram_dialog_manager.instance import ButtonInstance

from bot.models import AccessSettingsObject
from bot.dialogs.dialog_buttons import access_time_settings, back


def get_random_choice_game_access_settings_keyboard(settings_object: AccessSettingsObject, highlight_this: str = "") -> List[List[ButtonInstance]]:
    min_time_data = {"time": str(settings_object.min_punish_time_for_rand_choice).replace(' day,', '').replace(' days,', '')[:-3], "type": "min_time", "selected": highlight_this == "min_time"}
    max_time_data = {"time": str(settings_object.max_punish_time_for_rand_choice).replace(' day,', '').replace(' days,', '')[:-3], "type": "max_time", "selected": highlight_this == "max_time"}

    buttons = [
        [access_time_settings.get_instance(min_time_data)],
        [access_time_settings.get_instance(max_time_data)],
        [back.get_instance({"page": "game_menu"})]
    ]

    return buttons