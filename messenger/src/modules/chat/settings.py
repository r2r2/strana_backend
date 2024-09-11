from pydantic import BaseModel

from src.core.common.redis import RedisSettings


class ChatSettings(BaseModel):
    redis: RedisSettings
    is_user_in_chat_cache_ttl: int
    activity_throttle_time: int
    delivery_status_updated_throttle_time: int
    unread_message_delay_sec: int
