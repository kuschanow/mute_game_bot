from aiogram.fsm.state import StatesGroup, State


class RandomChoiceGameAccessSettingsStates(StatesGroup):
    set_min_time = State()
    set_max_time = State()

    @staticmethod
    def get_by_string(name: str):
        if name == "min_time":
            return RandomChoiceGameAccessSettingsStates.set_min_time
        if name == "max_time":
            return RandomChoiceGameAccessSettingsStates.set_max_time
