from aiogram.filters import Filter
from aiogram.fsm.context import FSMContext
from aiogram.types import Message


class ReplyToCorrectMessage(Filter):
    def __init__(self, key: str):
        self.key = key

    async def __call__(self, message: Message, state: FSMContext) -> bool:
        data = await state.get_data()
        if self.key not in data or message.reply_to_message is None:
            return False
        return message.reply_to_message.message_id == int(data[self.key])
