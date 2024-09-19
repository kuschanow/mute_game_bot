from typing import Dict, List, Tuple, Any

from bot.models.AccessSettingsObject import AccessSettingsObject
from games.models import RandomChoiceGame


def get_settings_keyboard(game: RandomChoiceGame, member_settings: AccessSettingsObject) -> List[List[Tuple[str, Dict[str, Any]]]]:
    return [
        [("is_creator_play", {"value": game.is_creator_playing})] if member_settings.can_join_games else [],
        [("min_max", {"state": "normal"})],
        [("losers", {"state": "normal"})],
        [("autostart_when_full", {"value": game.autostart_at_max_players})] if game.max_players_count else [],
        ["create"],
        ["cancel"]
    ]

async def get_game_menu_keyboard(game: RandomChoiceGame) -> List[List[str]]:
    buttons = [
        ["join"],
        ["delete"]
    ]

    if game.max_players_count >= await game.players.acount() >= game.min_players_count:
        buttons.insert(1, ["start"])

    return buttons


