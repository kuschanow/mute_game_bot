import random
from uuid import uuid4

from asgiref.sync import sync_to_async
from django.core.exceptions import ValidationError
from django.core.validators import MinValueValidator
from django.db import models
from django.db.models import F
from django.utils.translation import gettext as _

from bot.models import ChatMember
from shared.enums import AutoStartGame
from shared.utils import enum_to_choices


class RandomChoiceGame(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid4, editable=False)
    punishment = models.ForeignKey("Punishment", on_delete=models.CASCADE)
    min_players_count = models.PositiveIntegerField(null=False, default=2, validators=[MinValueValidator(2)])
    max_players_count = models.PositiveIntegerField(null=False, default=6)
    losers_count = models.PositiveIntegerField(null=False, default=1)

    creator = models.ForeignKey(ChatMember, null=True, blank=False, on_delete=models.SET_NULL, related_name="created_random_choice_games")
    players = models.ManyToManyField(ChatMember, through="RandomChoiceGamePlayer", related_name='participated_random_choice_games')
    is_creator_playing = models.BooleanField(default=True, null=False)

    auto_start_game = models.TextField(null=False, blank=False, choices=enum_to_choices(AutoStartGame), default=AutoStartGame.AT_MAX_PLAYERS.value)
    auto_start_at = models.DateTimeField(null=True, default=None)

    result = models.OneToOneField("RandomChoiceGameResult", null=True, default=None, on_delete=models.CASCADE, related_name="game")

    created_at = models.DateTimeField(auto_now_add=True)
    expire_at = models.DateTimeField(null=True, default=None)

    @sync_to_async
    def is_finished(self) -> bool:
        self.is_finished = self.result is not None
        return self.is_finished

    @sync_to_async
    def start_game(self):
        from . import RandomChoiceGameResult, RandomChoiceGameLoser
        losers = random.sample(list(self.players.annotate(player_id=F('randomchoicegameplayer__id')).all()), self.losers_count)

        game_result = RandomChoiceGameResult(game=self)
        game_result.save()

        for loser in losers:
            RandomChoiceGameLoser(player_id=loser.player_id, game_result=game_result).save()

        self.is_finished = True
        return game_result

    def get_string(self) -> str:
        # Translators: game to string
        return _("<b>Random choice game</b>\n\n" +
                 # Translators: game punishment
                 _("punishment: %(punishment)s\n" % {"punishment": self.punishment.get_string()}) +
                 # Translators: players diapason
                 _("👤: %(min)d - %(max)d\n" % {"min": self.min_players_count, "max": self.max_players_count}) +
                 # Translators: losers count
                 _("💀: %(losers)d\n\n" % {"losers": self.losers_count}) +
                 f"👑 {self.creator.get_string(True)}")

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

