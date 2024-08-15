from uuid import uuid4

from django.core.exceptions import ValidationError
from django.core.validators import MinValueValidator
from django.db import models

from shared.utils import enum_to_choices
from .Punishment import Punishment
from bot.models import User, ChatMember
from shared.enums import AutoStartGame


class RandomChoiceGame(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid4, editable=False)
    punishment = models.ForeignKey(Punishment, on_delete=models.CASCADE)
    min_players_count = models.PositiveIntegerField(null=False, default=2, validators=[MinValueValidator(2)])
    max_players_count = models.PositiveIntegerField(null=False, default=6)
    losers_count = models.PositiveIntegerField(null=False, default=1)

    creator = models.ForeignKey(ChatMember, null=False, blank=False, on_delete=models.CASCADE, related_name="created_random_choice_games")
    players = models.ManyToManyField(ChatMember, through="RandomChoiceGamePlayer", related_name='participated_random_choice_games')
    is_creator_playing = models.BooleanField(default=True, null=False)

    auto_start_game = models.TextField(null=False, blank=False, choices=enum_to_choices(AutoStartGame), default=AutoStartGame.AT_MAX_PLAYERS.value)
    auto_start_timer = models.DurationField(null=True, default=None)

    is_finished = models.BooleanField(null=False, default=False)

    created_at = models.DateTimeField(auto_now_add=True)
    expiration_timer = models.DurationField(null=True, default=None)

    def clean(self):
        cleaned_data = super().clean()
        min_players_count = cleaned_data.get("min_players_count")
        max_players_count = cleaned_data.get("max_players_count")
        is_creator_playing = cleaned_data.get("is_creator_playing")
        players_count = cleaned_data.get("players").count()
        losers_count = cleaned_data.get("losers_count")

        players_count = players_count + 1 if is_creator_playing else players_count

        if min_players_count > max_players_count:
            raise ValidationError(f"min players count cannot be greater than max players count")

        if players_count > max_players_count:
            raise ValidationError(f"players count cannot be greater than max players count")

        if losers_count < 1 or losers_count > max_players_count - 1:
            raise ValidationError(f"losers count must be less than max players count")

    def __str__(self):
        return f"[id {self.id}] - [creator {self.creator}] - [punishment {self.punishment}]"

