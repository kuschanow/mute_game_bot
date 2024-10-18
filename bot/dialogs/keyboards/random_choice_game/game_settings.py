from typing import List

from aiogram_dialog_manager.instance import ButtonInstance

from bot.models import AccessSettingsObject
from bot.dialogs.dialog_buttons import is_creator_play, min_max, losers, autostart_when_full, create, cancel
from games.models import RandomChoiceGame


def get_settings_keyboard(dialog, game: RandomChoiceGame, member_settings: AccessSettingsObject, min_max_state: str = "normal", losers_state: str = "normal") -> List[List[ButtonInstance]]:
    return [
        [is_creator_play.get_instance({"value": game.is_creator_playing})] if member_settings.can_join_games else [],
        [min_max.get_instance({"state": min_max_state}, dialog)],
        [losers.get_instance({"state": losers_state}, dialog)],
        [autostart_when_full.get_instance({"value": game.autostart_at_max_players})] if game.max_players_count else [],
        [create.get_instance({})],
        [cancel.get_instance()]
    ]
