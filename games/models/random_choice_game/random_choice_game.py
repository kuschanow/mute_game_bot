import random
from datetime import datetime, timezone

import humanize
from asgiref.sync import sync_to_async
from django.conf import settings
from django.core.exceptions import ValidationError
from django.core.validators import MinValueValidator
from django.db import models
from django.db.models import F
from django.utils.translation import gettext as _

from games.models.base_game_models import GameBase


class RandomChoiceGame(GameBase):
    game_name = "RandomChoice"

    min_players_count = models.PositiveIntegerField(null=False, default=2, validators=[MinValueValidator(2)])
    max_players_count = models.PositiveIntegerField(null=True, default=6)
    losers_count = models.PositiveIntegerField(null=False, default=1)

    autostart_at_max_players = models.BooleanField(null=False, default=False)
    autostart_operator = models.TextField(null=False, blank=False, default="or")
    autostart_timer = models.DurationField(null=True, default=None)
    autostart_timer_started_at = models.DateTimeField(null=True, default=None)

    @sync_to_async
    def start_game(self):
        from . import RandomChoiceGameResult, RandomChoiceGameLoser
        losers = random.sample(list(self.players.annotate(player_id=F('randomchoicegameplayer__id')).all()), self.losers_count)

        game_result = RandomChoiceGameResult(game=self)
        game_result.save()

        for loser in losers:
            RandomChoiceGameLoser(player_id=loser.player_id, game_result=game_result).save()

        self.save()
        return game_result

    @sync_to_async
    def get_string(self) -> str:
        when_full = _("when full")

        autostart_text = _("No")

        if self.autostart_at_max_players and self.autostart_timer is None:
            autostart_text = when_full
        elif self.autostart_timer is not None:
            if settings.HUMANIZE_LANGUAGE_CODE:
                humanize.i18n.activate(settings.HUMANIZE_LANGUAGE_CODE)
            start_after = humanize.naturaldelta((self.autostart_timer_started_at + self.autostart_timer - datetime.now(
                timezone.utc)) if self.autostart_timer_started_at or hasattr(self, "result") is not None else self.autostart_timer)

            if not self.autostart_at_max_players:
                autostart_text = _("after %(time)s") % {"time": self.autostart_timer}
            else:
                if self.autostart_operator == "or":
                    autostart_text = _("after %(time)s or %(full)s") % {"time": start_after, "full": when_full}
                else:
                    autostart_text = _("after %(time)s and %(full)s") % {"time": start_after, "full": when_full}

        return (_("<b>Random choice game</b>\n\n") +
                f"👑 {self.creator.get_string(True)}\n\n" +
                _("punishment: %(punishment)s\n") % {"punishment": self.punishment.get_string()} +
                _("👤: %(min)d - %(max)s\n") % {"min": self.min_players_count, "max": self.max_players_count or "♾"} +
                _("☠: %(losers)d\n\n") % {"losers": self.losers_count} +
                _("autostart: %(text)s") % {"text": autostart_text})

    def clean(self):
        players_count = self.players.count()

        players_count = players_count + 1 if self.is_creator_playing else players_count

        if self.min_players_count > self.max_players_count:
            raise ValidationError(f"min players count cannot be greater than max players count")

        if players_count > self.max_players_count:
            raise ValidationError(f"players count cannot be greater than max players count")

        if self.losers_count < 1 or self.losers_count > self.max_players_count - 1:
            raise ValidationError(f"losers count must be less than max players count")

        super().clean()
