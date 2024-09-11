from pydantic import BaseModel

from src.core.common.redis import RedisSettings
from src.modules.unread_counters.settings import UnreadCountersSettings


class UpdatesStreamerSettings(BaseModel):
    aud_whitelist: list[str]
    redis: RedisSettings
    unread_counters: UnreadCountersSettings
