from datetime import timedelta
from typing import List

from asgiref.sync import sync_to_async
from django.utils.translation import gettext as _

from bot.models import ChatMember
from django.conf import settings


def get_places(stats_list: List, page: int):
    places = stats_list[page * settings.RATING_PAGE_SIZE:(page + 1) * settings.RATING_PAGE_SIZE]

    if len(places) == 0:
        if page == 0:
            return None
        else:
            page = (len(stats_list) - 1) // settings.RATING_PAGE_SIZE
            places = stats_list[page * settings.RATING_PAGE_SIZE:(page + 1) * settings.RATING_PAGE_SIZE]

    return places

@sync_to_async
def get_top_time_text(stats_list: List[tuple[ChatMember, timedelta]], page: int) -> str:
    text = _("Random choice game rating by time:\n")
    if len(stats_list) == 0:
        return text

    places = get_places(stats_list, page)

    if places is None:
        return text

    for i in range(len(places)):
        text += f"    {page * settings.RATING_PAGE_SIZE + i + 1}) {places[i][0].get_string(True)}: {str(places[i][1]).replace(' days,', '')[:-3]}\n"

    return text

@sync_to_async
def get_top_count_text(stats_list: List[tuple[ChatMember, int, int]], page: int) -> str:
    text = _("Random choice game rating by played games count:\n")
    if len(stats_list) == 0:
        return text

    places = get_places(stats_list, page)

    if places is None:
        return text

    death_char = _("☠")

    for i in range(len(places)):
        text += f"    {page * settings.RATING_PAGE_SIZE + i + 1}) {places[i][0].get_string(True)}: {places[i][1]} ({death_char} {places[i][2]})\n"

    return text


def get_detailed_text(stats_list: List[tuple]) -> str:
    text = _("Random choice game detailed stats:\n")

    for stat in stats_list:
        text += f"    {stat[0]}: <strong>{stat[1]}</strong>\n"

    return text

@sync_to_async
def get_detailed_text_by_member(stats_list: List[tuple], member: ChatMember) -> str:
    text = _("%(member)s random choice game stats:\n" % {"member": member.get_string(True)})

    for stat in stats_list:
        text += f"    {stat[0]}: <strong>{stat[1]}</strong>\n"

    return text
