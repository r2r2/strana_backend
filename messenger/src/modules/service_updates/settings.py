from datetime import timedelta
from typing import Self

from pydantic import BaseModel, model_validator

from src.core.common.rabbitmq import AMQPConnectionSettings
from src.core.common.redis import RedisSettings


class UpdatesListenerCacheSettings(BaseModel):
    memory_cache_maxsize: int


class UpdatesListenerSettings(BaseModel):
    amqp: AMQPConnectionSettings
    publisher_redis: RedisSettings
    cache: UpdatesListenerCacheSettings
    queue_overflow_time_limit: int

    service_updates_rk: str
    publisher_max_concurrent_jobs: int
    publisher_max_pending_jobs: int
    publisher_jobs_warning_threshold: int

    updates_broadcast_extended_activity_time: timedelta

    @model_validator(mode="after")
    def validate_publisher_settings(self) -> Self:
        if self.publisher_jobs_warning_threshold > self.publisher_max_concurrent_jobs:
            raise ValueError(
                "Incorrect config: publisher_jobs_warning_threshold is bigger than publisher_max_concurrent_jobs",
            )

        return self
