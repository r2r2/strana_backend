from datetime import timedelta

from pydantic import Field

from src.core.common.redis.settings import RedisSettings
from src.jobs.base_settings import PeriodicJobSettings


class PresenceTrackerSettings(PeriodicJobSettings):
    redis: RedisSettings

    cleanup_interval: timedelta = Field(
        ...,
        description="Interval in seconds to clear the database from old activity data",
    )
    offline_time_threshold: timedelta = Field(
        ...,
        description="The time in seconds after which the user is considered offline when inactive",
    )
