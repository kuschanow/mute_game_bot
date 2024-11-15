from django.db import models


class HiddenMinesGameField(models.Model):
    id = models.UUIDField(primary_key=True, null=False, editable=False)

    game = models.ForeignKey("HiddenMinesGame", null=False, on_delete=models.CASCADE, related_name="field")
