from random import randint

from games.models.base_game_models import GameBase
from shared.enums.CellTypes import CellTypes
from .hidden_mines_game_cell import HiddenMinesGameCell
from .hidden_mines_game_field import HiddenMinesGameField


class HiddenMinesGame(GameBase):
    game_name = "HiddenMines"

    def get_random_2_by_2_field(self) -> HiddenMinesGameField:
        field = HiddenMinesGameField(game=self)
        field.save()
        cells = [
            HiddenMinesGameCell(x=0, y=0, field=field, type=CellTypes.MINE),
            HiddenMinesGameCell(x=1, y=0, field=field, type=CellTypes.MINE),
            HiddenMinesGameCell(x=0, y=1, field=field, type=CellTypes.MINE),
            HiddenMinesGameCell(x=1, y=1, field=field, type=CellTypes.MINE)
        ]

        cells[randint(0, 3)].type = CellTypes.EMPTY

        for cell in cells:
            cell.save()

        return field

    def get_string(self):
        return f"""
                {self.creator.get_string()}
                {_("Click on any button below this message")}

                {_("There are 3 'dead' cells and 1 'win' cell in the grid below")}
                """
