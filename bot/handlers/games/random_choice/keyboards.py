from typing import Dict
from uuid import uuid4
from django.conf import settings

from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from django.utils.translation import gettext as _

from bot.models import ChatMember
from games.models import Punishment


def get_punishment_categories_keyboard(dialog_id: uuid4) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            # Translators: private punishments button
            InlineKeyboardButton(text=_("Private"), callback_data=f"rcg:punish_category:0:1:{dialog_id}"),
            # Translators: chat punishments button
            InlineKeyboardButton(text=_("Public"), callback_data=f"rcg:punish_category:1:1:{dialog_id}"),
        ],
        [
            InlineKeyboardButton(text=_("Cancel"), callback_data=f"rcg:cancel:{dialog_id}"),
        ]
    ])

def get_punishments_keyboard(dialog_id: uuid4, chat_member: ChatMember, is_public: bool, page: int) -> (InlineKeyboardMarkup, Dict[int, Punishment]):
    start_index = (page - 1) * settings.PAGE_SIZE
    end_index = page * settings.PAGE_SIZE

    filters = {
        'is_public': is_public,
        'is_deleted': False
    }
    
    if is_public:
        filters['created_by__chat'] = chat_member.chat
    else:
        filters['created_by'] = chat_member

    query = Punishment.objects.filter(**filters)

    punishments = query[start_index:end_index]
    punishments_count = query.count()

    punishments_mapping = {}

    buttons = []
    for i in range(len(punishments)):
        p = punishments[i]
        h = p.time.total_seconds()//3600
        m = p.time.total_seconds//60 - h*60
        buttons.append([InlineKeyboardButton(text=f"{p.name} ({h}:{m}:00)",
                                             callback_data=f"rcg:punish_select:{i}:{dialog_id}")])
        punishments_mapping[i] = p

    navigation = [
        # Translators: change category
        InlineKeyboardButton(text=_("Category: %(category)s" % {"category": _("Public") if is_public else _("Private")}),
                             callback_data=f"rcg:punish_category:{int(not is_public)}:1:{dialog_id}")
    ]

    if page > 1:
        navigation.append(
            # Translators: previous page
            InlineKeyboardButton(text=_("Previous"), callback_data=f"rcg:punish_category:{is_public}:{page-1}:{dialog_id}")
        )
    if punishments_count - page * settings.PAGE_SIZE > 0:
        navigation.append(
            # Translators: next page
            InlineKeyboardButton(text=_("Next"), callback_data=f"rcg:punish_category:{is_public}:{page+1}:{dialog_id}")
        )

    buttons.append([navigation])
    buttons.append([
        InlineKeyboardButton(text=_("Cancel"), callback_data=f"rcg:cancel:{dialog_id}")
    ])

    return InlineKeyboardMarkup(inline_keyboard=buttons), punishments_mapping
