from typing import Dict
from uuid import uuid4

from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from asgiref.sync import sync_to_async
from django.conf import settings
from django.utils.translation import gettext as _

from bot.models import ChatMember
from bot.models.AccessSettingsObject import AccessSettingsObject
from games.models import Punishment


def get_punishment_privacy_selection_keyboard(handler_type: str, dialog_id: str, show_public: bool) -> InlineKeyboardMarkup:
    buttons = [
        [
            InlineKeyboardButton(text=_("Private Global"), callback_data=f"{handler_type}:-1:{dialog_id}"),
            InlineKeyboardButton(text=_("Private Local"), callback_data=f"{handler_type}:0:{dialog_id}")
        ],
        [
            InlineKeyboardButton(text=_("Cancel"), callback_data=f"{handler_type}:cancel:{dialog_id}"),
        ]
    ]

    if show_public:
        buttons.insert(1, [InlineKeyboardButton(text=_("Public"), callback_data=f"{handler_type}:1:{dialog_id}")])

    return InlineKeyboardMarkup(inline_keyboard=buttons)

def get_cancel_keyboard():
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text=_("Cancel"), callback_data=f"pc:cancel"),
        ]
    ])

@sync_to_async
def get_punishments_keyboard(dialog_id: uuid4, chat_member: ChatMember, member_settings: AccessSettingsObject, public_indicator: int, page: int) -> (InlineKeyboardMarkup, Dict[int, uuid4]):
    start_index = (page - 1) * settings.PAGE_SIZE
    end_index = page * settings.PAGE_SIZE

    filters = {
        'is_deleted': False,
        'is_public': public_indicator == 1,
    }

    if public_indicator > -1:
        filters['created_in'] = chat_member.chat
    else:
        filters['created_in__isnull'] = True
    if public_indicator < 1:
        filters['created_by'] = chat_member.user

    query = Punishment.objects.filter(**filters).order_by("time")

    punishments = query[start_index:end_index]
    punishments_count = query.count()

    if len(punishments) == 0 and page > 1:
        raise Exception("Invalid page number")

    punishments_mapping = {}

    buttons = []
    for i in range(len(punishments)):
        p = punishments[i]
        buttons.append([InlineKeyboardButton(text=p.get_string(), callback_data=f"pd:p_select:{i}:{dialog_id}")])
        punishments_mapping[i] = str(p.id)

    navigation = [
        InlineKeyboardButton(text=_("Private Global"), callback_data=f"pd:p_category:-1:1:{dialog_id}"),
        InlineKeyboardButton(text=_("Private Local"), callback_data=f"pd:p_category:0:1:{dialog_id}"),
    ]

    if member_settings.can_delete_public_punishments:
        navigation.append(InlineKeyboardButton(text=_("Public"), callback_data=f"pd:p_category:1:1:{dialog_id}"))

    navigation.pop(public_indicator + 1)

    if page > 1:
        navigation.insert(0,
            # Translators: previous page
            InlineKeyboardButton(text=_("Previous"), callback_data=f"pd:p_category:{public_indicator}:{page-1}:{dialog_id}")
        )
    if punishments_count - page * settings.PAGE_SIZE > 0:
        navigation.append(
            # Translators: next page
            InlineKeyboardButton(text=_("Next"), callback_data=f"pd:p_category:{public_indicator}:{page+1}:{dialog_id}")
        )

    buttons.append(navigation)
    buttons.append([
        InlineKeyboardButton(text=_("Cancel"), callback_data=f"pd:cancel:{dialog_id}")
    ])

    return InlineKeyboardMarkup(inline_keyboard=buttons), punishments_mapping

def get_acceptance_keyboard(dialog_id: str) -> InlineKeyboardMarkup:
    buttons = [
        [
            InlineKeyboardButton(text=_("Accept"), callback_data=f"pd:accept:{dialog_id}"),
        ],
        [
            InlineKeyboardButton(text=_("Cancel"), callback_data=f"pd:refuse:{dialog_id}"),
        ]
    ]

    return InlineKeyboardMarkup(inline_keyboard=buttons)
