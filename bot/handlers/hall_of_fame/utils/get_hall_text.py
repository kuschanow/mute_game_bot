from datetime import datetime, timezone
from typing import List

from asgiref.sync import sync_to_async
from django.utils.translation import gettext as _

from games.models import RandomChoiceGameLoser


@sync_to_async
def get_hall_text(losers: List[RandomChoiceGameLoser]) -> str:
    text = _("<b>Hall of Fame</b>\n\n%(losers_text)s")

    losers_text = ""

    losers = sorted(losers, key=lambda x: x.game_result.game.punishment.time)

    current_time = datetime.now(timezone.utc)

    for i in range(len(losers)):
        loser = losers[i]
        left = str(loser.game_result.finished_at + loser.game_result.game.punishment.time - current_time)
        losers_text += (f"{i + 1}) {loser.player.chat_member.get_string()} <b>total:</b> {loser.game_result.game.punishment.get_string()} / "
                        f"<b>left</b>: {left.replace(' day,', '').replace(' days,', '')[:-(left.index('.'))]}\n")

    return text % {"losers_text": losers_text}
