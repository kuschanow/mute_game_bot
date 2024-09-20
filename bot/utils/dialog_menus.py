from typing import List

from aiogram_dialog_manager.instance import ButtonInstance
from aiogram_dialog_manager.prototype import MenuPrototype

from bot.models import AccessSettingsObject
from bot.utils import get_punishments_keyboard
from bot.utils.dialog_buttons import cancel as cancel_button, privacy as privacy_button, accept as accept_button, refuse, join, delete, \
    is_creator_play, min_max, losers, autostart_when_full, create, start
from games.models import RandomChoiceGame


def get_settings_keyboard(dialog, game: RandomChoiceGame, member_settings: AccessSettingsObject, min_max_state: str = "normal", losers_state: str = "normal") -> List[List[ButtonInstance]]:
    return [
        [is_creator_play.get_instance({"value": game.is_creator_playing})] if member_settings.can_join_games else [],
        [min_max.get_instance({"state": min_max_state}, dialog)],
        [losers.get_instance({"state": losers_state}, dialog)],
        [autostart_when_full.get_instance({"value": game.autostart_at_max_players})] if game.max_players_count else [],
        [create.get_instance()],
        [cancel_button.get_instance()]
    ]

async def get_game_menu_keyboard(game: RandomChoiceGame) -> List[List[ButtonInstance]]:
    buttons = [
        [join.get_instance()],
        [delete.get_instance()]
    ]

    if game.max_players_count >= await game.players.acount() >= game.min_players_count:
        buttons.insert(1, [start.get_instance()])

    return buttons


cancel = MenuPrototype("cancel", lambda: [[cancel_button.get_instance()]])

privacy = MenuPrototype("privacy", lambda settings: [
    [privacy_button.get_instance({"public_indicator": -1}), privacy_button.get_instance({"public_indicator": 0})],
    [privacy_button.get_instance({"public_indicator": 1})] if settings.can_create_public_punishments else [],
    [cancel_button.get_instance()]
])

punishments = MenuPrototype("punishments", get_punishments_keyboard)

accept = MenuPrototype("accept", lambda p_id: [[accept_button.get_instance({"id": p_id})], [refuse.get_instance()]])

random_choice_settings = MenuPrototype("random_choice_settings", get_settings_keyboard)

random_choice_game = MenuPrototype("random_choice_game", get_game_menu_keyboard)
