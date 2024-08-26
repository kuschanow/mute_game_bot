from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from django.utils.translation import gettext as _

from bot.models.AccessSettingsObject import AccessSettingsObject


def get_punishment_privacy_selection_keyboard(dialog_id: str, member_settings: AccessSettingsObject) -> InlineKeyboardMarkup:
    buttons =[
        [
            InlineKeyboardButton(text=_("Private Global"), callback_data=f"pc:-1:{dialog_id}"),
            InlineKeyboardButton(text=_("Private Local"), callback_data=f"pc:0:{dialog_id}")
        ],
        [
            InlineKeyboardButton(text=_("Cancel"), callback_data=f"pc:cancel:{dialog_id}"),
        ]
    ]

    if member_settings.can_create_public_punishments:
        buttons.insert(1, [InlineKeyboardButton(text=_("Public"), callback_data=f"pc:1:{dialog_id}")])

    return InlineKeyboardMarkup(inline_keyboard=buttons)

def get_cancel_keyboard():
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text=_("Cancel"), callback_data=f"pc:cancel"),
        ]
    ])
