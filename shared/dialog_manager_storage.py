from aiogram_dialog_manager.storage import MemoryStorage, RedisStorage
from django.conf import settings

if settings.REDIS_HOST and settings.REDIS_PORT:
    from redis.asyncio.client import Redis

    r = Redis(host=settings.REDIS_HOST, port=settings.REDIS_PORT, db=settings.REDIS_DIALOG_DB, decode_responses=True)
    storage = RedisStorage(r)
else:
    storage = MemoryStorage()
