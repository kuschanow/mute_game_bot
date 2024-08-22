from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from django.utils.translation import gettext as _

from bot.models import Chat


def get_chat_settings_keyboard(chat: Chat) -> InlineKeyboardMarkup:
    buttons = [
        [
            InlineKeyboardButton(
                text=_("Admins can play %(status)s" % {"status": '✅' if chat.can_admins_join_games else '☑️'}),
                callback_data="chat_settings:can_admins_join_games")
        ],
        [
            InlineKeyboardButton(
                text=_("Admins can create games %(status)s" % {"status": '✅' if chat.can_admins_create_games else '☑️'}),
                callback_data="chat_settings:can_admins_create_games")
        ],
        [
            InlineKeyboardButton(
                text=_("Admins can press other buttons %(status)s" % {"status": '✅' if chat.can_admins_press_other_buttons else '☑️'}),
                callback_data="chat_settings:can_admins_press_other_buttons")
        ],
        [
            InlineKeyboardButton(
                text=_("Admins ignore time limits %(status)s" % {"status": '✅' if chat.can_admins_ignore_time_limitations else '☑️'}),
                callback_data="chat_settings:can_admins_ignore_time_limitations")
        ],
        [
            InlineKeyboardButton(
                text=_("All can create punishments %(status)s" % {"status": '✅' if chat.can_members_create_public_punishments else '☑️'}),
                callback_data="chat_settings:can_members_create_public_punishments")
        ],
        [
          InlineKeyboardButton(
              text=_("Games settings"),
              callback_data="chat_settings:games_menu"
          )
        ],
    ]

    return InlineKeyboardMarkup(inline_keyboard=buttons)
