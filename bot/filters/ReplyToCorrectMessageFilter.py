from aiogram.filters import Filter
from aiogram.fsm.context import FSMContext
from aiogram.types import Message


class ReplayToCorrectMessageFilter(Filter):
    def __init__(self, message_name: str):
        self.message_name = message_name

    async def __call__(self, message: Message, state: FSMContext) -> bool:
        data = await state.get_data()
        if "punish_creation" not in data or message.reply_to_message is None:
            return False
        return message.reply_to_message.message_id == int(data["punish_creation"][self.message_name])
