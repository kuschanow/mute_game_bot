from typing import Dict
from uuid import uuid4

from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from asgiref.sync import sync_to_async
from django.conf import settings
from django.utils.translation import gettext as _

from bot.models import ChatMember
from bot.models.AccessSettingsObject import AccessSettingsObject
from games.models import Punishment, RandomChoiceGame


@sync_to_async
def get_punishments_keyboard(chat_member: ChatMember, member_settings: AccessSettingsObject, public_indicator: int, page: int) -> InlineKeyboardMarkup:
    start_index = page * settings.PAGE_SIZE
    end_index = page + 1 * settings.PAGE_SIZE

    filters = {
        'is_deleted': False,
        'is_public': public_indicator == 1,
        'time__gte': member_settings.min_punish_time_for_rand_choice
    }

    if public_indicator > -1:
        filters['created_in'] = chat_member.chat
    else:
        filters['created_in__isnull'] = True
    if public_indicator < 1:
        filters['created_by'] = chat_member.user
    if member_settings.max_punish_time_for_rand_choice is not None:
        filters["time__lte"] = member_settings.max_punish_time_for_rand_choice

    query = Punishment.objects.filter(**filters).order_by("time")

    punishments = query[start_index:end_index]
    punishments_count = query.count()

    buttons = []
    for p in punishments:
        buttons.append([InlineKeyboardButton(text=p.get_string(), callback_data=f"rcgc:p_select:{p.id}")])

    navigation = [
        InlineKeyboardButton(text=_("Private Global"), callback_data=f"rcgc:p_category:-1:0"),
        InlineKeyboardButton(text=_("Private Local"), callback_data=f"rcgc:p_category:0:0"),
        InlineKeyboardButton(text=_("Public"), callback_data=f"rcgc:p_category:1:0"),
    ]

    navigation.pop(public_indicator + 1)

    if page > 0:
        navigation.insert(0,
            # Translators: previous page
            InlineKeyboardButton(text=_("Previous"), callback_data=f"rcgc:p_category:{public_indicator}:{page-1}")
        )
    if punishments_count - (page + 1) * settings.PAGE_SIZE > 0:
        navigation.append(
            # Translators: next page
            InlineKeyboardButton(text=_("Next"), callback_data=f"rcgc:p_category:{public_indicator}:{page+1}")
        )

    buttons.append(navigation)
    buttons.append([
        InlineKeyboardButton(text=_("Cancel"), callback_data=f"rcgc:cancel")
    ])

    return InlineKeyboardMarkup(inline_keyboard=buttons)

def get_game_settings_keyboard(game: RandomChoiceGame, member_settings: AccessSettingsObject, highlight_this: str = "") -> InlineKeyboardMarkup:
    min_max_text = _("Min-Max players: %(min)d-%(max)d" % {"min": game.min_players_count, "max": game.max_players_count})
    losers_text = _("Losers count: %(count)s" % {"count": game.losers_count})

    if highlight_this == "min_max":
        min_max_text = _("▶ %(text)s ◀" % {"text": min_max_text})
    if highlight_this == "losers":
        losers_text = _("▶ %(text)s ◀" % {"text": losers_text})

    buttons = [
        [
            InlineKeyboardButton(text=_("%(indicator)s Add creator as player"
                                        % {"indicator": '🚫' if not member_settings.can_join_games else ('✅' if game.is_creator_playing else '☑️')}),
                                 callback_data=f"rcgs:is_creator_play:{game.id}")
        ],
        [
            InlineKeyboardButton(text=min_max_text,
                                 callback_data=f"rcgs:min_max:{game.id}"),
        ],
        [
            InlineKeyboardButton(text=losers_text,
                                 callback_data=f"rcgs:losers:{game.id}"),
        ],
        [
            InlineKeyboardButton(text=_("Autostart when full %(indicator)s"
                                        % {"indicator": '🚫' if game.max_players_count is None else ('✅' if game.autostart_at_max_players else '☑️')}),
                                 callback_data=f"rcgs:when_full:{game.id}"),
        ],
        [
            InlineKeyboardButton(text=_("Create game"),
                                 callback_data=f"rcgs:create:{game.id}"),
        ],
        [
            InlineKeyboardButton(text=_("Cancel"),
                                 callback_data=f"rcgs:cancel_creation:{game.id}"),
        ]
    ]

    return InlineKeyboardMarkup(inline_keyboard=buttons)

async def get_game_menu_keyboard(game: RandomChoiceGame) -> InlineKeyboardMarkup:
    buttons = [
        [
            # Translators: join game button
            InlineKeyboardButton(text=_("Join/Left"), callback_data=f"rcg:join:{game.id}")
        ],
        [
            # Translators: delete
            InlineKeyboardButton(text=_("Delete"), callback_data=f"rcg:delete:{game.id}"),
        ]
    ]

    if game.max_players_count >= await game.players.acount() >= game.min_players_count:
        # Translators: start game button
        buttons.insert(1, [InlineKeyboardButton(text=_("Start"), callback_data=f"rcg:start:{game.id}")])

    return InlineKeyboardMarkup(inline_keyboard=buttons)


