from aiogram.filters import Filter
from aiogram.types import CallbackQuery


class DialogAccessFilter(Filter):
    def __init__(self, dialog_id: str) -> None:
        self.dialog_id = dialog_id

    async def __call__(self, callback: CallbackQuery) -> bool:
        pass
