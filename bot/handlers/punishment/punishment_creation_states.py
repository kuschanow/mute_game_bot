from aiogram.fsm.state import StatesGroup, State


class PunishmentCreationStates(StatesGroup):
    choosing_name = State()
    choosing_time = State()