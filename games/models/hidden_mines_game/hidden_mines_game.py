from random import randint

from asgiref.sync import sync_to_async
from django.utils.translation import gettext as _

from games.models.base_game_models import GameBase
from shared.enums.CellTypes import CellTypes
from .hidden_mines_game_cell import HiddenMinesGameCell
from .hidden_mines_game_field import HiddenMinesGameField
from .hidden_mines_game_result import HiddenMinesGameResult
from .hidden_mines_game_winner import HiddenMinesGameWinner
from .hidden_mines_game_loser import  HiddenMinesGameLoser


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

        cells[randint(0, 3)].type = CellTypes.WIN

        for cell in cells:
            cell.save()

        return field

    def get_string(self):
        return f"""
                {self.creator.get_string()}
                {_("Click on any button below this message")}

                {_("There are 3 'dead' cells and 1 'win' cell in the grid below")}
                """

    async def finish_game_by_timeout(self) -> HiddenMinesGameResult:
        result = HiddenMinesGameResult(game=self)
        await result.asave()

        loser = HiddenMinesGameLoser(game_result=result, player=await sync_to_async(self.players.first)())
        await loser.asave()

        return result

    async def finish_game(self, with_cell: HiddenMinesGameCell) -> HiddenMinesGameResult:
        result = HiddenMinesGameResult(game=self)
        await result.asave()

        if with_cell.type == CellTypes.WIN:
            winner = HiddenMinesGameWinner(game_result=result, player=await sync_to_async(self.players.first)())
            await winner.asave()

        elif with_cell.type == CellTypes.MINE:
            loser = HiddenMinesGameLoser(game_result=result, player=await sync_to_async(self.players.first)())
            await loser.asave()

        return result
