from aiogram.client.default import DefaultBotProperties
from django.conf import settings

from aiogram import Bot, Dispatcher
from aiogram.enums.parse_mode import ParseMode

bot = Bot(token=settings.BOT_TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML, link_preview_is_disabled=True))

if settings.REDIS_HOST and settings.REDIS_PORT:
    from aiogram.fsm.storage.redis import RedisStorage, DefaultKeyBuilder
    from redis.asyncio.client import Redis

    r = Redis(host=settings.REDIS_HOST, port=settings.REDIS_PORT, db=settings.REDIS_FSM_DB, decode_responses=True)
    storage = RedisStorage(redis=r, key_builder=DefaultKeyBuilder())
else:
    from aiogram.fsm.storage.memory import MemoryStorage

    storage = MemoryStorage()

dp = Dispatcher(storage=storage)
