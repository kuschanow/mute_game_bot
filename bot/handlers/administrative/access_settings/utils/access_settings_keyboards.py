from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from django.utils.translation import gettext as _

from bot.models import Chat, AccessSettingsObject


def get_settings_targets_keyboard() -> InlineKeyboardMarkup:
    buttons = [
        [
            InlineKeyboardButton(text=_("Global"), callback_data="stgs:targets:chat")
        ],
        [
            InlineKeyboardButton(text=_("Admins"), callback_data="stgs:targets:admins")
        ],
        # [
        #     InlineKeyboardButton(text=_("Groups"), callback_data="stgs:settings_targets:group")
        # ],
        # [
        #     InlineKeyboardButton(text=_("Individual"), callback_data="stgs:settings_targets:member")
        # ],
    ]

    return InlineKeyboardMarkup(inline_keyboard=buttons)

def get_settings_keyboard(settings_object: AccessSettingsObject | None, _type: int) -> InlineKeyboardMarkup:
    if settings_object is None:
        buttons = [
            [
                InlineKeyboardButton(
                    text=_("Make different from global"),
                    callback_data=f"stgs:{_type}:make_diff")
            ],
            [
                InlineKeyboardButton(
                    text=_("Back"),
                    callback_data="stgs:targets"
                )
            ]
        ]
    else:
        buttons = [
            [
                InlineKeyboardButton(
                    text=_("Can play %(status)s" % {"status": '✅' if settings_object.can_join_games else '☑️'}),
                    callback_data=f"stgs:{_type}:join_games:{settings_object.id}")
            ],
            [
                InlineKeyboardButton(
                    text=_("Can create games %(status)s" % {"status": '✅' if settings_object.can_create_games else '☑️'}),
                    callback_data=f"stgs:{_type}:create_games:{settings_object.id}")
            ],
            [
                InlineKeyboardButton(
                    text=_("Can press other buttons %(status)s" % {"status": '✅' if settings_object.can_press_other_buttons else '☑️'}),
                    callback_data=f"stgs:{_type}:press_other_buttons:{settings_object.id}")
            ],
            [
                InlineKeyboardButton(
                    text=_("Can create punishments %(status)s" % {"status": '✅' if settings_object.can_create_public_punishments else '☑️'}),
                    callback_data=f"stgs:{_type}:create_punishments:{settings_object.id}")
            ],
            [
                InlineKeyboardButton(
                    text=_("Can delete punishments %(status)s" % {"status": '✅' if settings_object.can_delete_public_punishments else '☑️'}),
                    callback_data=f"stgs:{_type}:delete_punishments:{settings_object.id}")
            ],
            [
                InlineKeyboardButton(
                    text=_("Games settings"),
                    callback_data=f"stgs:{_type}:games_menu:{settings_object.id}"
                )
            ],
            [
                InlineKeyboardButton(
                    text=_("Back"),
                    callback_data="stgs:targets"
                )
            ]
        ]

        if _type > 0:
            buttons.insert(-2, [InlineKeyboardButton(text=_("Reset to global"), callback_data=f"stgs:{_type}:clear")])

    return InlineKeyboardMarkup(inline_keyboard=buttons)

