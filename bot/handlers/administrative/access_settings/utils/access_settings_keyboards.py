from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from django.utils.translation import gettext as _

from bot.models import Chat, AccessSettingsObject
from shared import target


def get_settings_targets_keyboard() -> InlineKeyboardMarkup:
    buttons = [
        [
            InlineKeyboardButton(text=target["chat"], callback_data=f"stgs:targets:chat")
        ],
        [
            InlineKeyboardButton(text=target["admins"], callback_data=f"stgs:targets:admins")
        ],
        # [
        #     InlineKeyboardButton(text=_("Groups"), callback_data="stgs:settings_targets:group")
        # ],
        # [
        #     InlineKeyboardButton(text=_("Individual"), callback_data="stgs:settings_targets:member")
        # ],
    ]

    return InlineKeyboardMarkup(inline_keyboard=buttons)

def get_settings_keyboard(settings_object: AccessSettingsObject | None, target_id: str) -> InlineKeyboardMarkup:
    if settings_object is None:
        buttons = [
            [
                InlineKeyboardButton(
                    text=_("Make different from global"),
                    callback_data=f"stgs:{target_id}:make_diff")
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
                    text=_("Can play %(status)s" ) % {"status": '✅' if settings_object.can_join_games else '☑️'},
                    callback_data=f"stgs:{target_id}:join_games:set")
            ],
            [
                InlineKeyboardButton(
                    text=_("Can create games %(status)s" ) % {"status": '✅' if settings_object.can_create_games else '☑️'},
                    callback_data=f"stgs:{target_id}:create_games:set")
            ],
            [
                InlineKeyboardButton(
                    text=_("Can press other buttons %(status)s" ) % {"status": '✅' if settings_object.can_press_other_buttons else '☑️'},
                    callback_data=f"stgs:{target_id}:press_other_buttons:set")
            ],
            [
                InlineKeyboardButton(
                    text=_("Can create punishments %(status)s" ) % {"status": '✅' if settings_object.can_create_public_punishments else '☑️'},
                    callback_data=f"stgs:{target_id}:create_punishments:set")
            ],
            [
                InlineKeyboardButton(
                    text=_("Can delete punishments %(status)s" ) % {"status": '✅' if settings_object.can_delete_public_punishments else '☑️'},
                    callback_data=f"stgs:{target_id}:delete_punishments:set")
            ],
            [
                InlineKeyboardButton(
                    text=_("Games settings"),
                    callback_data=f"stgs:{target_id}:games_menu"
                )
            ],
            [
                InlineKeyboardButton(
                    text=_("Back"),
                    callback_data="stgs:targets"
                )
            ]
        ]

        if target_id != "chat":
            buttons.insert(-2, [InlineKeyboardButton(text=_("Reset to global"), callback_data=f"stgs:{target_id}:clear")])

    return InlineKeyboardMarkup(inline_keyboard=buttons)

def get_games_select_keyboard(target_id: str) -> InlineKeyboardMarkup:
    buttons = [
        [
            InlineKeyboardButton(
                text=_("Random choice game"),
                callback_data=f"stgs:games_menu:{target_id}:rcg")
        ],
        [
            InlineKeyboardButton(
                text=_("Back"),
                callback_data=f"stgs:targets:{target_id}"
            )
        ]
    ]

    return InlineKeyboardMarkup(inline_keyboard=buttons)

def get_random_choice_game_settings_keyboard(settings_object: AccessSettingsObject, target_id: str, highlight_this: str = "") -> InlineKeyboardMarkup:
    min_time_text = _("Min time: %(time)s") % {"time": str(settings_object.min_punish_time_for_rand_choice).replace(' days,', '')[:-3]}
    max_time_text = _("Max time: %(time)s") % {"time": str(settings_object.max_punish_time_for_rand_choice).replace(' days,', '')[:-3]}

    if highlight_this == "min_time":
        min_time_text = _("▶ %(text)s ◀") % {"text": min_time_text}
    if highlight_this == "max_time":
        max_time_text = _("▶ %(text)s ◀") % {"text": max_time_text}

    buttons = [
        [
            InlineKeyboardButton(
                text=min_time_text,
                callback_data=f"stgs:games:rcg:{target_id}:min_time")
        ],
        [
            InlineKeyboardButton(
                text=max_time_text,
                callback_data=f"stgs:games:rcg:{target_id}:max_time")
        ],
        [
            InlineKeyboardButton(
                text=_("Back"),
                callback_data=f"stgs:{target_id}:games_menu"
            )
        ]
    ]

    return InlineKeyboardMarkup(inline_keyboard=buttons)

