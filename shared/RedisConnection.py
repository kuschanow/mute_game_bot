import json

from django.conf import settings
from redis.asyncio.client import Redis


class RedisConnection(Redis):
    async def get_or_set(self, name: str):
        data = await self.get(name)
        if data is None:
            await self.set(name, "{}")
        return data

    async def get_deserialized(self, name: str):
        data = await self.get(name)
        return json.loads(data) if data is not None else None

    async def set_serialized(self, name: str, data):
        await self.set(name, json.dumps(data))

redis = RedisConnection(host=settings.REDIS_HOST, port=settings.REDIS_PORT, db=settings.REDIS_DB)
