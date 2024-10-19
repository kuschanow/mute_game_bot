from datetime import timedelta
from typing import List

from asgiref.sync import sync_to_async, async_to_sync
from django.conf import settings
from django.db.models import Sum, F, Count, Case, When, IntegerField, ExpressionWrapper, fields
from django.db.models.functions import Extract
from django.utils.translation import gettext as _

from bot.models import Chat, ChatMember
from games.models import RandomChoiceGameLoser, RandomChoiceGamePlayer, RandomChoiceGame


@sync_to_async
def get_random_choice_game_time_stats(chat: Chat) -> List[tuple[ChatMember, timedelta]]:
    members_stats = (
        RandomChoiceGameLoser.objects
        .filter(player__chat_member__chat_id=chat.id)
        .values('player__chat_member_id')
        .annotate(total_time=Sum(F('game_result__game__punishment__time'), output_field=fields.PositiveIntegerField()) / 1_000_000)
    ) if settings.USE_SQLITE else (
        RandomChoiceGameLoser.objects
        .filter(player__chat_member__chat_id=chat.id)
        .values('player__chat_member_id')
        .annotate(total_time=Sum(Extract('game_result__game__punishment__time', 'EPOCH'), output_field=fields.PositiveIntegerField()))
    )

    result = [
        (ChatMember.objects.get(id=stat['player__chat_member_id']), timedelta(seconds=stat['total_time']))
        for stat in members_stats
    ]

    result = [(unit[0], unit[1]) for unit in result if async_to_sync(lambda: unit[0].access_settings)().show_in_stats]

    return sorted(result, key=lambda x: x[1], reverse=True)


@sync_to_async
def get_random_choice_game_count_stats(chat: Chat) -> List[tuple[ChatMember, int, int]]:
    members_stats = (
        RandomChoiceGamePlayer.objects
        .filter(chat_member__chat_id=chat.id, game__result__isnull=False)
        .values('chat_member_id')
        .annotate(
            total_games=Count('id'),
            losses=Count(Case(When(randomchoicegameloser__isnull=False, then=1), output_field=IntegerField()))
        )
    )

    result = [
        (ChatMember.objects.get(id=stat['chat_member_id']), stat['total_games'], stat['losses'])
        for stat in members_stats
    ]

    result = [(unit[0], unit[1], unit[2]) for unit in result if async_to_sync(lambda: unit[0].access_settings)().show_in_stats]

    return sorted(result, key=lambda x: x[1], reverse=True)


async def get_random_choice_game_detailed_stats(chat: Chat) -> List[tuple]:
    games = RandomChoiceGame.objects.filter(creator__chat=chat, result__isnull=False)
    total_games = await games.acount()

    total_time_seconds = sum([unit[1].total_seconds() for unit in await get_random_choice_game_time_stats(chat)])
    total_time = timedelta(seconds=total_time_seconds)

    return [(_("Total games count"), total_games),
            (_("Total time in mute"), str(total_time).replace(' day,', '').replace(' days,', '')[:-3])]


@sync_to_async
def get_random_choice_game_detailed_stats_by_user(member: ChatMember) -> List[tuple]:
    games = RandomChoiceGamePlayer.objects.filter(chat_member=member, game__result__isnull=False)
    total_games = games.count()
    lost_games = games.filter(randomchoicegameloser__isnull=False).count()
    created_games = RandomChoiceGame.objects.filter(creator=member).count()
    total_time_seconds = (
            games
            .filter(randomchoicegameloser__isnull=False)
            .annotate(punishment_seconds=ExpressionWrapper(F('game__punishment__time'), output_field=fields.PositiveIntegerField()))
            .annotate(punishment_time=F('punishment_seconds') / 1_000_000)
            .aggregate(total_seconds=Sum('punishment_time'))['total_seconds']
            or 0
    ) if settings.USE_SQLITE else (
            games
            .filter(randomchoicegameloser__isnull=False)
            .annotate(punishment_seconds=ExpressionWrapper(Extract('game__punishment__time', 'EPOCH'), output_field=fields.PositiveIntegerField()))
            .annotate(punishment_time=F('punishment_seconds'))
            .aggregate(total_seconds=Sum('punishment_time'))['total_seconds']
            or 0
    )
    total_time = timedelta(seconds=total_time_seconds)

    return [(_("Total games count"), total_games),
            (_("Lost games count"), lost_games), 
            (_("Created games count"), created_games),
            (_("Total time in mute"), str(total_time).replace(' day,', '').replace(' days,', '')[:-3])]
