from random import randint

from django.db import models

from shared.enums.CellTypes import CellTypes
from .hidden_mines_game import HiddenMinesGame
from .hidden_mines_game_cell import HiddenMinesGameCell


class HiddenMinesGameField(models.Model):
    id = models.UUIDField(primary_key=True, null=False, editable=False)

    game = models.ForeignKey("HiddenMinesGame", null=False, on_delete=models.CASCADE, related_name="field")
