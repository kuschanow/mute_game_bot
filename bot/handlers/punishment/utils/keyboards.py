from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from django.utils.translation import gettext as _


def get_punishment_privacy_selection_keyboard(dialog_id: str) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text=_("Private Global"), callback_data=f"pc:-1:{dialog_id}"),
            InlineKeyboardButton(text=_("Private Local"), callback_data=f"pc:0:{dialog_id}")
        ],
        [
            InlineKeyboardButton(text=_("Public"), callback_data=f"pc:1:{dialog_id}"),
        ],
        [
            InlineKeyboardButton(text=_("Cancel"), callback_data=f"pc:cancel:{dialog_id}"),
        ]
    ])

def get_cancel_keyboard():
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text=_("Cancel"), callback_data=f"pc:cancel"),
        ]
    ])
