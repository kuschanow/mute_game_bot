import random
from datetime import datetime
from uuid import uuid4

from asgiref.sync import sync_to_async
from django.core.exceptions import ValidationError
from django.core.validators import MinValueValidator
from django.db import models
from django.db.models import F
from django.utils.translation import gettext as _

from bot.models import ChatMember


class RandomChoiceGame(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid4, editable=False)
    punishment = models.ForeignKey("Punishment", on_delete=models.CASCADE)
    min_players_count = models.PositiveIntegerField(null=False, default=2, validators=[MinValueValidator(2)])
    max_players_count = models.PositiveIntegerField(null=True, default=6)
    losers_count = models.PositiveIntegerField(null=False, default=1)

    creator = models.ForeignKey(ChatMember, null=True, blank=False, on_delete=models.SET_NULL, related_name="created_random_choice_games")
    players = models.ManyToManyField(ChatMember, through="RandomChoiceGamePlayer", related_name='participated_random_choice_games')
    is_creator_playing = models.BooleanField(default=True, null=False)

    autostart_at_max_players = models.BooleanField(null=False, default=False)
    autostart_operator = models.TextField(null=False, blank=False, default="or")
    autostart_at = models.DateTimeField(null=True, default=None)

    is_opened_to_join = models.BooleanField(null=False, default=False)

    result = models.OneToOneField("RandomChoiceGameResult", null=True, default=None, on_delete=models.CASCADE, related_name="game")

    created_at = models.DateTimeField(auto_now_add=True)

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
        self.result = game_result
        self.save()
        return game_result

    @sync_to_async
    def get_string(self) -> str:
        when_full = _("when full")

        autostart_text = _("No")

        if self.autostart_at_max_players and self.autostart_at is None:
            autostart_text = when_full
        elif self.autostart_at is not None:
            if self.autostart_at.date() == datetime.now().date():
                at_time = _("%(time)s" % {"time": self.autostart_at.strftime("%H:%M:%S")})
            else:
                at_time = _("%(time)s" % {"time": self.autostart_at.strftime("%Y-%m-%d %H:%M:%S")})

            if not self.autostart_at_max_players:
                autostart_text = _("at %(time)s" % {"time": at_time})
            else:
                if self.autostart_operator == "or":
                    autostart_text = _("if time is %(time)s or %(full)s" % {"time": at_time, "full": when_full})
                else:
                    autostart_text = _("if the time is greater than %(time)s and %(full)s" % {"time": at_time, "full": when_full})

        # Translators: game to string
        return (_("<b>Random choice game</b>\n\n") +
                # Translators: game punishment
                _("punishment: %(punishment)s\n" % {"punishment": self.punishment.get_string()}) +
                # Translators: players diapason
                _("👤: %(min)d - %(max)d\n" % {"min": self.min_players_count, "max": self.max_players_count}) +
                # Translators: losers count
                _("☠: %(losers)d\n\n" % {"losers": self.losers_count}) +
                _("autostart: %(text)s\n\n" % {"text": autostart_text}) +
                f"👑 {self.creator.get_string(True)}")

    def clean(self):
        players_count = self.players.count()

        players_count = players_count + 1 if self.is_creator_playing else players_count

        if self.min_players_count > self.max_players_count:
            raise ValidationError(f"min players count cannot be greater than max players count")

        if players_count > self.max_players_count:
            raise ValidationError(f"players count cannot be greater than max players count")

        if self.losers_count < 1 or self.losers_count > self.max_players_count - 1:
            raise ValidationError(f"losers count must be less than max players count")

    def __str__(self):
        return f"[id {self.id}] - [creator {self.creator}] - [punishment {self.punishment}]"

