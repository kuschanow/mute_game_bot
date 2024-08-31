from aiogram.fsm.state import StatesGroup, State


class GameSettingsStates(StatesGroup):
    set_min_max = State()
    set_losers = State()
    set_autostart_time = State()

    @staticmethod
    def get_be_string(name: str):
        if name == "min_max":
            return GameSettingsStates.set_min_max
        if name == "losers":
            return GameSettingsStates.set_losers
        if name == "autostart_time":
            return GameSettingsStates.set_autostart_time
