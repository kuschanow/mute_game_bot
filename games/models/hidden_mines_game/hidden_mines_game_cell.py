import uuid

from django.db import models

from shared.enums.CellTypes import CellTypes
from shared.utils import enum_to_choices


class HiddenMinesGameCell(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    x = models.IntegerField(null=False)
    y = models.IntegerField(null=False)

    type = models.TextField(null=False, blank=False, choices=enum_to_choices(CellTypes), default=CellTypes.WIN.value)

    is_opened = models.BooleanField(null=False, default=False)

    field = models.ForeignKey("HiddenMinesGameField", null=False, blank=False, on_delete=models.CASCADE, related_name="cells")
