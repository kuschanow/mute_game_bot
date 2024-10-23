from datetime import datetime
from typing import List
from datetime import timezone

from asgiref.sync import sync_to_async

from bot.models import Chat
from games.models import RandomChoiceGameLoser


@sync_to_async
def get_current_punished(chat: Chat) -> List[RandomChoiceGameLoser]:
    current_time = datetime.now(timezone.utc)

    query = RandomChoiceGameLoser.objects.filter(game_result__game__creator__chat_id=chat.id)

    result = list([loser for loser in query if loser.game_result.finished_at + loser.game_result.game.punishment.time > current_time])

    return result
