from django.db import models

from games.models import HiddenMinesGame
from bot.dialogs.dialog_buttons import cell


def get_game_field(game: HiddenMinesGame):
    field = []

    max_y = game.field.cells.all().aggregate(models.Max('y'))['y__max']
    max_x = game.field.cells.all().aggregate(models.Max('x'))['x__max']

    for y in range(max_y + 1):
        row = []
        for x in range(max_x + 1):
            cell_instance = game.field.cells.filter(x=x, y=y).first()
            if cell_instance:
                row.append(cell.get_instance({"is_opened": cell_instance.is_opened, "type": cell_instance.type, "id": cell_instance.id}))
            else:
                raise Exception("Cell not found")
        field.append(row)

    return field
