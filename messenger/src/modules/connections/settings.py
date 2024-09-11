from pydantic import BaseModel

from src.core.common.redis import RedisSettings


class ConnectionsServiceSettings(BaseModel):
    redis: RedisSettings
