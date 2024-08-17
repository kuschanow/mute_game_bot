from typing import Dict
from uuid import uuid4

from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from asgiref.sync import sync_to_async
from django.conf import settings
from django.utils.translation import gettext as _

from bot.models import ChatMember
from games.models import Punishment


def get_punishment_privacy_selection_keyboard(dialog_id: str) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text=_("Private"), callback_data=f"pc:0:{dialog_id}"),
            InlineKeyboardButton(text=_("Public"), callback_data=f"pc:1:{dialog_id}"),
        ],
        [
            InlineKeyboardButton(text=_("Cancel"), callback_data=f"pc:cancel:{dialog_id}"),
        ]
    ])

