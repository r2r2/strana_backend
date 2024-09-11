from datetime import timedelta

from src.core.common.rabbitmq import AMQPConnectionSettings
from src.jobs.base_settings import JobSettings


class MatchStateUpdatesListenerSettings(JobSettings):
    amqp: AMQPConnectionSettings
    updates_exchange_name: str
    queue_name: str
    finish_match_update_delay: timedelta
