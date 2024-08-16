from aiogram.filters import Filter
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery


class DialogAccessFilter(Filter):
    async def __call__(self, callback_query: CallbackQuery, state: FSMContext) -> bool:
        data = await state.get_data()
        if "dialogs" not in data:
            return False
        return callback_query.data.split(':')[-1] in data["dialogs"]
