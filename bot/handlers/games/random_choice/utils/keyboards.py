from typing import Dict
from uuid import uuid4

from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from asgiref.sync import sync_to_async
from django.conf import settings
from django.utils.translation import gettext as _

from bot.models import ChatMember
from games.models import Punishment


def get_punishment_categories_keyboard(dialog_id: uuid4) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            # Translators: private
            InlineKeyboardButton(text=_("Private"), callback_data=f"rcgc:p_category:0:1:{dialog_id}"),
            # Translators: public
            InlineKeyboardButton(text=_("Public"), callback_data=f"rcgc:p_category:1:1:{dialog_id}"),
        ],
        [
            # Translators: cancel
            InlineKeyboardButton(text=_("Cancel"), callback_data=f"rcgc:cancel:{dialog_id}"),
        ]
    ])

@sync_to_async
def get_punishments_keyboard(dialog_id: uuid4, chat_member: ChatMember, is_public: bool, page: int) -> (InlineKeyboardMarkup, Dict[int, uuid4]):
    start_index = (page - 1) * settings.PAGE_SIZE
    end_index = page * settings.PAGE_SIZE

    filters = {
        'is_deleted': False
    }
    
    if is_public:
        filters['created_by__chat'] = chat_member.chat
        filters['is_public'] = is_public
    else:
        filters['created_by'] = chat_member

    query = Punishment.objects.filter(**filters)

    punishments = query[start_index:end_index]
    punishments_count = query.count()

    punishments_mapping = {}

    buttons = []
    for i in range(len(punishments)):
        p = punishments[i]
        buttons.append([InlineKeyboardButton(text=p.get_string(), callback_data=f"rcgc:p_select:{i}:{dialog_id}")])
        punishments_mapping[i] = str(p.id)

    navigation = [
        # Translators: change category
        InlineKeyboardButton(text=_("%(category)s" % {"category": _("Private") if is_public else _("Public")}),
                             callback_data=f"rcgc:p_category:{int(not is_public)}:1:{dialog_id}")
    ]

    if page > 1:
        navigation.insert(0,
            # Translators: previous page
            InlineKeyboardButton(text=_("Previous"), callback_data=f"rcgc:p_category:{int(is_public)}:{page-1}:{dialog_id}")
        )
    if punishments_count - page * settings.PAGE_SIZE > 0:
        navigation.append(
            # Translators: next page
            InlineKeyboardButton(text=_("Next"), callback_data=f"rcgc:p_category:{int(is_public)}:{page+1}:{dialog_id}")
        )

    buttons.append(navigation)
    buttons.append([
        InlineKeyboardButton(text=_("Cancel"), callback_data=f"rcgc:cancel:{dialog_id}")
    ])

    return InlineKeyboardMarkup(inline_keyboard=buttons), punishments_mapping

def get_game_menu_keyboard(game_id: uuid4) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            # Translators: join game button
            InlineKeyboardButton(text=_("Join/Left"), callback_data=f"rcg:join:{game_id}")
        ],
        [
            # Translators: start game button
            InlineKeyboardButton(text=_("Start"), callback_data=f"rcg:start:{game_id}")
        ],
        [
            # Translators: delete
            InlineKeyboardButton(text=_("Delete"), callback_data=f"rcg:delete:{game_id}"),
        ]
    ])


