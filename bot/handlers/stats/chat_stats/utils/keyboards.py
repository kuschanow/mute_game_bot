from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from asgiref.sync import sync_to_async
from django.conf import settings
from django.db.models import Min
from django.utils.translation import gettext as _

from bot.models import Chat
from games.models import RandomChoiceGameLoser

@sync_to_async
def get_top_stats_keyboard(chat: Chat, page: int, category: str) -> InlineKeyboardMarkup:
    buttons = [
        [
            InlineKeyboardButton(text=_("▶ Top ◀"), callback_data=f"stats:chat:top:{page}:{category}"),
            InlineKeyboardButton(text=_("Detailed"), callback_data="stats:chat:detailed")
        ]
    ]

    if settings.USE_SQLITE:
        query = RandomChoiceGameLoser.objects.filter(player__chat_member__chat_id=chat.id)\
                .values('player__chat_member_id') \
                .annotate(min_id=Min('id')) \
                .distinct()
    else:
        query = RandomChoiceGameLoser.objects.filter(player__chat_member__chat_id=chat.id).distinct("player__chat_member_id")

    navigation = []

    if page > 0:
        navigation.append(InlineKeyboardButton(text=_("First"), callback_data=f"stats:chat:top:0:{category}"))
        navigation.append(InlineKeyboardButton(text=_("Previous"), callback_data=f"stats:chat:top:{page - 1}:{category}"))

    if len(query[page * settings.RATING_PAGE_SIZE:]) > settings.RATING_PAGE_SIZE:
        navigation.append(InlineKeyboardButton(text=_("Next"), callback_data=f"stats:chat:top:{page + 1}:{category}"))
        navigation.append(InlineKeyboardButton(text=_("Last"), callback_data=f"stats:chat:top:{((query.count() - 1) // settings.RATING_PAGE_SIZE) if query.count() else 0}:{category}"))

    buttons.append(navigation)

    time_category_text = _("By time")
    games_count_category_text = _("By games")

    if category == "time":
        time_category_text = _("▶ %(text)s ◀" ) % {"text": time_category_text}
    else:
        games_count_category_text = _("▶ %(text)s ◀" ) % {"text": games_count_category_text}

    buttons.append([
        InlineKeyboardButton(text=time_category_text, callback_data=f"stats:chat:top:{page}:time"),
        InlineKeyboardButton(text=games_count_category_text, callback_data=f"stats:chat:top:{page}:count")
    ])

    return InlineKeyboardMarkup(inline_keyboard=buttons)


def get_detailed_stats_keyboard() -> InlineKeyboardMarkup:
    buttons = [
        [
            InlineKeyboardButton(text=_("Top"), callback_data="stats:chat:top:0:time"),
            InlineKeyboardButton(text=_("▶ Detailed ◀"), callback_data="stats:chat:detailed")
        ]
    ]

    return InlineKeyboardMarkup(inline_keyboard=buttons)

