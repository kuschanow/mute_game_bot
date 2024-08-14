from enum import Enum

class AutoStartGame(Enum):
    NO = "no"
    AT_MAX_PLAYERS = "at_max_players"
    BY_TIMER = "by_timer"
    AT_MAX_PLAYERS_AND_BY_TIMER = "at_max_players_and_by_timer"
    AT_MAX_PLAYERS_OR_BY_TIMER = "at_max_players_or_by_timer"
