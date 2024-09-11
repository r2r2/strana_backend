import pickle
from typing import Any, Generic, Iterable, Mapping, TypeVar

from cachetools import LRUCache

from src.core.types import RedisConn

KeyT = TypeVar("KeyT", bound=str)
ValueT = TypeVar("ValueT")


class LayeredCache(Generic[KeyT, ValueT]):
    def __init__(
        self,
        maxsize: int,
        ttl: int,
        redis: RedisConn,
    ) -> None:
        self.ttl = ttl
        self.maxsize = maxsize
        self._redis = redis
        self._memory_cache = LRUCache(maxsize=maxsize)

    async def get(self, key: KeyT) -> ValueT | None:
        if (stored := self._memory_cache.get(key)) is not None:
            return stored

        in_redis = await self._get_from_redis(key)
        if in_redis is not None:
            self._memory_cache[key] = in_redis

        return in_redis

    async def set(self, key: KeyT, value: ValueT) -> None:  # noqa: A003
        self._memory_cache[key] = value
        await self._set_in_redis(key, value)

    async def get_multi(self, keys: list[KeyT]) -> dict[KeyT, ValueT]:
        result = {}
        for key in keys:
            if in_memory := self._memory_cache.get(key):
                result[key] = in_memory

        missing_ids = set(keys) - set(result.keys())
        if missing_ids:
            in_redis = await self._get_multiple_from_redis(missing_ids)
            self._memory_cache.update(in_redis)
            result.update(in_redis)

        return result

    async def set_multi(self, data: dict[KeyT, ValueT]) -> None:
        self._memory_cache.update(data)
        await self._set_multiple_in_redis(data)

    async def _get_from_redis(self, key: KeyT) -> ValueT | None:
        raw_data = await self._redis.get(key)
        if raw_data:
            return pickle.loads(raw_data)  # noqa: S301

        return None

    async def _set_in_redis(self, key: KeyT, value: ValueT) -> None:
        await self._redis.set(key, pickle.dumps(value), ex=int(self.ttl))

    async def _get_multiple_from_redis(self, keys: Iterable[KeyT]) -> dict[KeyT, ValueT]:
        return {
            key: pickle.loads(raw_data)  # noqa: S301
            for key, raw_data in zip(
                keys,
                await self._redis.mget(*keys),
                strict=True,
            )
            if raw_data
        }

    async def _set_multiple_in_redis(self, data: dict[KeyT, ValueT]) -> None:
        if not data:
            return

        pipeline = self._redis.pipeline()
        updates: Mapping[Any, Any] = {key: pickle.dumps(value) for key, value in data.items()}
        pipeline.mset(updates)
        for user_key in updates:
            pipeline.expire(user_key, int(self.ttl))

        await pipeline.execute()
