from aiogram.fsm.state import StatesGroup, State


class AccessGroupStates(StatesGroup):
    set_name = State()
    change_name = State()
