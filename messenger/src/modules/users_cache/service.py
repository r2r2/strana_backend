import pickle
from typing import Any, Iterable, Mapping
from uuid import uuid4

from cachetools import TTLCache

from src.core.common.redis.helpers import create_redis_conn_pool
from src.core.common.redis.pubsub import RedisListener
from src.core.common.utility import PatternStrEnum
from src.core.logger import LoggerName, get_logger
from src.entities.redis import RedisPubSubChannelName
from src.entities.users import UserData
from src.modules.users_cache.interface import UsersCacheProtocol
from src.modules.users_cache.settings import UsersCacheSettings


class UserCacheKey(PatternStrEnum):
    DATA = "userdata:[{user_id}]"


class UsersCacheService(UsersCacheProtocol):
    """Layered cache for users data."""

    def __init__(
        self,
        settings: UsersCacheSettings,
    ) -> None:
        self.settings = settings
        self.logger = get_logger(LoggerName.USERS_CACHE)
        self._memory_cache = TTLCache[int, UserData](
            maxsize=self.settings.memory_cache.max_size,
            ttl=self.settings.memory_cache.ttl,
        )
        self._redis_conn = create_redis_conn_pool(settings.redis)
        self._id = str(uuid4())

    async def start(self) -> None:
        self.updates_listener = RedisListener(
            conn=self._redis_conn,
            callback=self._handle_cache_invalidation,
        )
        await self.updates_listener.start()
        await self.updates_listener.subscribe(RedisPubSubChannelName.USER_DATA_CACHE_INVALIDATION.value)

    async def stop(self) -> None:
        await self.updates_listener.stop()

    async def _handle_cache_invalidation(self, update: bytes) -> None:
        update_str = update.decode()
        updated_by_id, user_id = update_str.split(":", maxsplit=1)
        if updated_by_id != self._id:
            self.logger.debug(f"Invalidating memory cache for user {user_id}")
            self._memory_cache.pop(int(user_id), None)

    async def get(self, user_id: int) -> UserData | None:
        if user_data := self._memory_cache.get(user_id):
            return user_data

        in_redis = await self._get_from_redis(user_id)
        if in_redis:
            self._memory_cache[user_id] = in_redis

        return in_redis

    async def set(self, user_id: int, data: UserData) -> None:  # noqa: A003
        self._memory_cache[user_id] = data
        await self._set_in_redis(user_id, data)

    async def get_multiple(self, user_ids: list[int]) -> dict[int, UserData]:
        result = {}
        for user_id in user_ids:
            if user_data := self._memory_cache.get(user_id):
                result[user_id] = user_data.model_copy()

        missing_ids = set(user_ids) - set(result.keys())
        if missing_ids:
            in_redis = await self._get_multiple_from_redis(missing_ids)
            self._memory_cache.update(in_redis)
            result.update({key: value.model_copy() for key, value in in_redis.items()})

        return result

    async def set_multiple(self, data: dict[int, UserData]) -> None:
        self._memory_cache.update(data)
        await self._set_multiple_in_redis(data)

    async def _get_from_redis(self, user_id: int) -> UserData | None:
        raw_data = await self._redis_conn.get(UserCacheKey.DATA.format(user_id=user_id))
        if raw_data:
            try:
                return pickle.loads(raw_data)  # noqa: S301
            except Exception:
                self.logger.warning(f"Failed to get user data from Redis for user {user_id}", exc_info=True)
                return None

        return None

    async def _set_in_redis(self, user_id: int, data: UserData) -> None:
        await self._redis_conn.set(
            UserCacheKey.DATA.format(user_id=user_id), pickle.dumps(data), ex=int(self.settings.redis_cache.ttl)
        )

    async def _get_multiple_from_redis(self, user_ids: Iterable[int]) -> dict[int, UserData]:
        try:
            return {
                user_id: pickle.loads(raw_data)  # noqa: S301
                for user_id, raw_data in zip(
                    user_ids,
                    await self._redis_conn.mget([UserCacheKey.DATA.format(user_id=user_id) for user_id in user_ids]),
                    strict=True,
                )
                if raw_data
            }
        except Exception:
            self.logger.warning("Failed to get multiple users data from Redis", exc_info=True)
            return {}

    async def _set_multiple_in_redis(self, data: dict[int, UserData]) -> None:
        if not data:
            return

        pipeline = self._redis_conn.pipeline()
        updates: Mapping[Any, Any] = {
            UserCacheKey.DATA.format(user_id=user_id): pickle.dumps(user_data) for user_id, user_data in data.items()
        }
        pipeline.mset(updates)
        for user_key in updates:
            pipeline.expire(user_key, int(self.settings.redis_cache.ttl))

        await pipeline.execute()
