from aiogram import Router, F
from aiogram.types import CallbackQuery

from bot.filters import DialogAccess
from bot.handlers.stats.chat_stats.utils.keyboards import get_top_stats_keyboard
from bot.handlers.stats.chat_stats.utils.stats import get_random_choice_game_time_stats, get_random_choice_game_count_stats
from bot.handlers.stats.chat_stats.utils.texts import get_top_time_text, get_top_count_text
from bot.models import Chat

chat_stats_top_router = Router()
chat_stats_top_router.callback_query.filter(F.data.startswith("stats:chat:top"))


@chat_stats_top_router.callback_query()
async def top_stats(callback: CallbackQuery, chat: Chat):
    data = callback.data.split(":")[3:]
    page = int(data[0])
    category = data[1]

    if category == "time":
        text = await get_top_time_text(await get_random_choice_game_time_stats(chat), page)
    else:
        text = await get_top_count_text(await get_random_choice_game_count_stats(chat) , page)

    try:
        await callback.message.edit_text(text=text, reply_markup=await get_top_stats_keyboard(chat, page, category))
    except:
        pass

    await callback.answer()

