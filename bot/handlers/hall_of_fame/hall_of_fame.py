from aiogram import Router, F
from aiogram.enums import ChatType
from aiogram.filters import MagicData, Command
from aiogram.types import Message, CallbackQuery
from aiogram_dialog_manager import DialogManager, Dialog
from aiogram_dialog_manager.filter import DialogFilter, ButtonFilter
from django.conf import settings

from bot.dialogs.dialog_buttons import update as update_button
from bot.dialogs.dialog_menus import update
from bot.handlers.hall_of_fame.utils import get_hall_text, get_current_punished
from bot.models import Chat

hall_of_fame_board_router = Router()
hall_of_fame_board_router.callback_query.filter(DialogFilter("hall_of_fame"))
hall_of_fame_board_router.message.filter(MagicData(F.chat.type.is_not(ChatType.PRIVATE)))


@hall_of_fame_board_router.message(Command(settings.HALL_OF_FAME_COMMAND))
async def hall_of_fame_command(message: Message, chat: Chat, dialog_manager: DialogManager, bot):
    dialog = Dialog.create("hall_of_fame", message.from_user.id, chat.id, bot)

    await dialog.send_message(await get_hall_text(await get_current_punished(chat)), update)

    await dialog_manager.save_dialog(dialog)

    await message.delete()


@hall_of_fame_board_router.callback_query(ButtonFilter(update_button))
async def update_board(callback: CallbackQuery, dialog: Dialog, chat: Chat):
    await callback.answer()

    await dialog.edit_message(callback.message.message_id, await get_hall_text(await get_current_punished(chat)), update)
