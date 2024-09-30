from datetime import timedelta

from aiogram.enums import ChatType
from asgiref.sync import async_to_sync
from future.backports.datetime import datetime

from bot.generate_session import bot
from bot.models import ChatMember
from games.models import RandomChoiceGame


def collect_garbage():
    pass
