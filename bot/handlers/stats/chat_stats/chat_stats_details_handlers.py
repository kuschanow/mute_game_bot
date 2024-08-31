from aiogram import Router, F
from aiogram.enums import ParseMode
from aiogram.types import CallbackQuery

from bot.filters import DialogAccess
from bot.handlers.stats.chat_stats.utils.keyboards import get_detailed_stats_keyboard
from bot.handlers.stats.chat_stats.utils.stats import get_random_choice_game_detailed_stats
from bot.handlers.stats.chat_stats.utils.texts import get_detailed_text
from bot.models import Chat

chat_stats_detailed_router = Router()
chat_stats_detailed_router.callback_query.filter(F.data.startswith("stats:chat:detailed"), DialogAccess())


@chat_stats_detailed_router.callback_query()
async def top_stats(callback: CallbackQuery, chat: Chat):
    try:
        await callback.message.edit_text(text=get_detailed_text(await get_random_choice_game_detailed_stats(chat)),
                                         reply_markup=get_detailed_stats_keyboard())
    except:
        pass

    await callback.answer()

