from datetime import timedelta

from pydantic import BaseModel, SecretStr

from src.core.common.rabbitmq import AMQPConnectionSettings


class PushNotificationsVapidSettings(BaseModel):
    private_key: SecretStr
    email: str
    token_ttl: int


class RetrySettings(BaseModel):
    max_attempts: int = 3
    wait_exp_multiplier: float = 2
    max_wait_time: float = 5
    wait_exp_base: float = 1


class PushNotificationsSenderSettings(BaseModel):
    vapid: PushNotificationsVapidSettings
    send_push_request_timeout: float = 5.0


class PushNotificationsListenerSettings(BaseModel):
    amqp_conn: AMQPConnectionSettings
    retries: RetrySettings
    message_preview_length: int
    device_last_alive_threshold: timedelta


class PushNotificationEventsPublisherSettings(BaseModel):
    amqp_conn: AMQPConnectionSettings
    rk: str
