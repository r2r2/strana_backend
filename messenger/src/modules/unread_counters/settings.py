from pydantic import BaseModel

from src.core.common.redis import RedisSettings


class UnreadCountersSettings(BaseModel):
    redis: RedisSettings
    counters_ttl: int = 86400  # 1 day
