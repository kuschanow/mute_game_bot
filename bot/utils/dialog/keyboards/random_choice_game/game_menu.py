from typing import List

from aiogram_dialog_manager.instance.button import ButtonInstance

from bot.utils.dialog.dialog_buttons import join, delete, start
from games.models import RandomChoiceGame


async def get_game_menu_keyboard(game: RandomChoiceGame) -> List[List[ButtonInstance]]:
    buttons = [
        [join.get_instance()],
        [delete.get_instance()]
    ]

    if game.max_players_count >= await game.players.acount() >= game.min_players_count:
        buttons.insert(1, [start.get_instance()])

    return buttons