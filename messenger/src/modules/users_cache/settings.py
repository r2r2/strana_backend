from pydantic import BaseModel

from src.core.common.caching import CacheSettings
from src.core.common.redis.settings import RedisSettings


class UsersCacheSettings(BaseModel):
    memory_cache: CacheSettings
    redis_cache: CacheSettings
    redis: RedisSettings
