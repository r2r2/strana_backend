from datetime import timedelta

from pydantic import BaseModel, Field

from src.core.common.redis import RedisSettings


class PresenceSettings(BaseModel):
    redis: RedisSettings

    activity_time_threshold: timedelta = Field(
        ...,
        description="Time in seconds during which the user is considered active and receives notifications",
    )
