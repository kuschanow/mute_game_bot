from aiogram import Router, F
from aiogram.enums.chat_type import ChatType
from aiogram.filters import Command, MagicData
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery
from aiogram_dialog_manager import Dialog, DialogManager
from aiogram_dialog_manager.filter import ButtonFilter
from aiogram_dialog_manager.instance import ButtonInstance
from django.conf import settings
from django.utils.translation import gettext as _

from bot.generate_session import bot
from bot.models import Chat, User
from bot.utils.dialog.dialog_buttons import stats_format, stats_category, change_page
from bot.utils.dialog.dialog_menus import stats
from bot.utils.dialog.dialog_texts import base_dialog_text
from .utils.stats import get_random_choice_game_time_stats, get_random_choice_game_detailed_stats, get_random_choice_game_count_stats
from .utils.texts import get_top_time_text, get_detailed_text, get_top_count_text

chat_stats_router = Router()
chat_stats_router.message.filter(MagicData(F.chat.type.is_not(ChatType.PRIVATE)))


async def stats_by_time(chat, page) -> str:
    return await get_top_time_text(await get_random_choice_game_time_stats(chat), page)

async def stats_by_games(chat, page) -> str:
    return await get_top_count_text(await get_random_choice_game_count_stats(chat) , page)


@chat_stats_router.message(Command(settings.SHOW_CHAT_STATS_COMMAND))
async def chat_stats_command(message: Message, chat: Chat, state: FSMContext, user: User, dialog_manager: DialogManager):
    await state.clear()

    dialog = Dialog.create("chat_stats", user_id=user.id, chat_id=chat.id, bot=bot)
    dialog.data["prefix"] = _("Dialog with ") + user.get_string(True) + "\n\n"
    dialog.data["format"] = "top"
    dialog.data["category"] = "by_time"
    dialog.data["page"] = 0
    dialog.temp["text"] = await stats_by_time(chat, dialog.data["page"])
    await dialog.send_message(base_dialog_text, stats)
    await dialog_manager.save_dialog(dialog)
    await message.delete()


@chat_stats_router.callback_query(ButtonFilter(stats_format, format="top"))
async def top_stats(callback: CallbackQuery, chat: Chat, dialog: Dialog):
    await callback.answer()
    dialog.data["format"] = "top"
    dialog.data["category"] = "by_time"
    dialog.data["page"] = 0
    dialog.temp["text"] = await stats_by_time(chat, dialog.data["page"])
    try:
        await dialog.edit_message(callback.message.message_id, base_dialog_text, stats)
    except:
        pass


@chat_stats_router.callback_query(ButtonFilter(stats_category))
async def top_by_time(callback: CallbackQuery, chat: Chat, dialog: Dialog, button: ButtonInstance):
    dialog.data["category"] = button.data["category"]
    dialog.temp["text"] = await (stats_by_time(chat, dialog.data["page"]) if dialog.values["category"] == "by_time" else stats_by_games(chat, dialog.data["page"]))
    try:
        await dialog.edit_message(callback.message.message_id, base_dialog_text, stats)
    except:
        pass


@chat_stats_router.callback_query(ButtonFilter(change_page))
async def change_page(callback: CallbackQuery, chat: Chat, dialog: Dialog, button: ButtonInstance):
    dialog.data["page"] = button.data["page"]
    dialog.temp["text"] = await (stats_by_time(chat, dialog.data["page"]) if dialog.values["category"] == "by_time" else stats_by_games(chat, dialog.data["page"]))
    try:
        await dialog.edit_message(callback.message.message_id, base_dialog_text, stats)
    except:
        pass


@chat_stats_router.callback_query(ButtonFilter(stats_format, format="detailed"))
async def top_stats(callback: CallbackQuery, chat: Chat, dialog: Dialog):
    await callback.answer()
    dialog.data["format"] = "detailed"
    dialog.temp["text"] = get_detailed_text(await get_random_choice_game_detailed_stats(chat))
    try:
        await dialog.edit_message(callback.message.message_id, base_dialog_text, stats)
    except:
        pass

