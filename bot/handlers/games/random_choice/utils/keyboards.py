from typing import Dict
from uuid import uuid4

from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from asgiref.sync import sync_to_async
from django.conf import settings
from django.utils.translation import gettext as _

from bot.models import ChatMember
from bot.models.SettingsObject import SettingsObject
from games.models import Punishment, RandomChoiceGame


@sync_to_async
def get_punishments_keyboard(dialog_id: uuid4, chat_member: ChatMember, member_settings: SettingsObject, public_indicator: int, page: int) -> (InlineKeyboardMarkup, Dict[int, uuid4]):
    start_index = (page - 1) * settings.PAGE_SIZE
    end_index = page * settings.PAGE_SIZE

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

    punishments_mapping = {}

    buttons = []
    for i in range(len(punishments)):
        p = punishments[i]
        buttons.append([InlineKeyboardButton(text=p.get_string(), callback_data=f"rcgc:p_select:{i}:{dialog_id}")])
        punishments_mapping[i] = str(p.id)

    navigation = [
        InlineKeyboardButton(text=_("Private Global"), callback_data=f"rcgc:p_category:-1:1:{dialog_id}"),
        InlineKeyboardButton(text=_("Private Local"), callback_data=f"rcgc:p_category:0:1:{dialog_id}"),
        InlineKeyboardButton(text=_("Public"), callback_data=f"rcgc:p_category:1:1:{dialog_id}"),
    ]

    navigation.pop(public_indicator + 1)

    if page > 1:
        navigation.insert(0,
            # Translators: previous page
            InlineKeyboardButton(text=_("Previous"), callback_data=f"rcgc:p_category:{public_indicator}:{page-1}:{dialog_id}")
        )
    if punishments_count - page * settings.PAGE_SIZE > 0:
        navigation.append(
            # Translators: next page
            InlineKeyboardButton(text=_("Next"), callback_data=f"rcgc:p_category:{public_indicator}:{page+1}:{dialog_id}")
        )

    buttons.append(navigation)
    buttons.append([
        InlineKeyboardButton(text=_("Cancel"), callback_data=f"rcgc:cancel:{dialog_id}")
    ])

    return InlineKeyboardMarkup(inline_keyboard=buttons), punishments_mapping


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


