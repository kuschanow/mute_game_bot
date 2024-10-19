from typing import List

from aiogram_dialog_manager import Dialog
from aiogram_dialog_manager.instance import ButtonInstance
from asgiref.sync import sync_to_async
from django.conf import settings
from django.db.models import Min
from django.utils.translation import gettext as _

from bot.dialogs.dialog_buttons import stats_format, change_page, stats_category, cancel
from games.models import RandomChoiceGameLoser


@sync_to_async
def get_stats_keyboard(dialog: Dialog) -> List[List[ButtonInstance]]:
    page = dialog.values["page"]
    category = dialog.values["category"]
    _format = dialog.values["format"]

    buttons = [
        [
            stats_format.get_instance({"state": "selected" if _format == "top" else "normal", "format": "top", "format_name": _("Top")}),
            stats_format.get_instance({"state": "selected" if _format == "detailed" else "normal", "format": "detailed", "format_name": _("Detailed")})
        ]
    ]

    if settings.USE_SQLITE:
        query = RandomChoiceGameLoser.objects.filter(player__chat_member__chat_id=dialog.chat_id) \
            .values('player__chat_member_id') \
            .annotate(min_id=Min('id')) \
            .distinct()
    else:
        query = RandomChoiceGameLoser.objects.filter(player__chat_member__chat_id=dialog.chat_id).distinct("player__chat_member_id")

    navigation = []

    if page > 0:
        navigation.append(change_page.get_instance({"to_page": "first", "page": 0}))
        navigation.append(change_page.get_instance({"to_page": "prev", "page": page - 1}))

    if len(query[page * settings.RATING_PAGE_SIZE:]) > settings.RATING_PAGE_SIZE:
        navigation.append(change_page.get_instance({"to_page": "next", "page": page + 1}))
        navigation.append(change_page.get_instance({"to_page": "last", "page": ((query.count() - 1) // settings.RATING_PAGE_SIZE) if query.count() else 0}))

    buttons.append(navigation)

    if _format == "top":
        buttons.append([
            stats_category.get_instance({"state": "selected" if category == "by_time" else "normal", "category": "by_time", "category_name": _("By time")}),
            stats_category.get_instance({"state": "selected" if category == "by_games" else "normal", "category": "by_games", "category_name": _("By games")})
        ])
    buttons.append([cancel.get_instance()])

    return buttons
