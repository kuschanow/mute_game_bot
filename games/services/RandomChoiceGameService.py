from bot.models import User, Chat
from games.models import RandomChoiceGame


class RandomChoiceGameService:
    def __init__(self, game_instance: RandomChoiceGame):
        self.instance = game_instance

    @staticmethod
    async def create_game(user: User, chat: Chat) -> RandomChoiceGame:
        pass

