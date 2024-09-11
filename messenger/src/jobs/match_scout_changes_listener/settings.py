from src.core.common.rabbitmq import AMQPConnectionSettings
from src.jobs.base_settings import JobSettings


class MatchScoutChangesListenerSettings(JobSettings):
    amqp: AMQPConnectionSettings
    updates_exchange_name: str
    queue_name: str
