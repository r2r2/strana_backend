import asyncio

from aio_pika import ExchangeType
from tenacity import AsyncRetrying, retry_if_exception_type, wait_exponential
from tenacity.stop import stop_after_attempt
from web_pusher.exceptions import InvalidEndpointError, TryAgainLaterError

from src.core.common import ProtectedProperty
from src.core.common.rabbitmq import ConnectionHolder, ListenerAMQPArgs, QueueListener
from src.core.logger import LoggerName, get_logger
from src.exceptions import InternalError
from src.modules.storage import StorageServiceProto

from .handlers.base import BaseUpdateHandler, PreparedPushNotification
from .interface import (
    PushNotificationsListenerProto,
    PushNotificationsRMQOpts,
    PushNotificationsSenderProto,
    SendPushQueueMessage,
)
from .settings import PushNotificationsListenerSettings


class PushNotificationsListener(PushNotificationsListenerProto):
    _amqp_conn = ProtectedProperty[ConnectionHolder]()
    _updates_listener = ProtectedProperty[QueueListener[SendPushQueueMessage]]()

    def __init__(
        self,
        sender: PushNotificationsSenderProto,
        settings: PushNotificationsListenerSettings,
        storage: StorageServiceProto,
    ) -> None:
        self.logger = get_logger(LoggerName.PUSH_LISTENER)
        self.storage = storage

        self._settings = settings
        self._amqp_conn = ConnectionHolder(
            settings=self._settings.amqp_conn,
            logger=self.logger.bind(subtype="conn_holder"),
        )
        self._sender = sender

        self._retrier = AsyncRetrying(
            retry_error_callback=lambda _: None,
            retry=retry_if_exception_type(TryAgainLaterError),
            stop=stop_after_attempt(self._settings.retries.max_attempts),
            wait=wait_exponential(
                multiplier=self._settings.retries.wait_exp_multiplier,
                max=self._settings.retries.max_wait_time,
                exp_base=self._settings.retries.wait_exp_base,
            ),
        )

    async def health_check(self) -> bool:
        return self._updates_listener.is_running

    async def start(self) -> None:
        await self._sender.start()
        await self._amqp_conn.start()
        self._updates_listener = await QueueListener.create(
            amqp_args=ListenerAMQPArgs(
                exchange_durable=True,
                exchange_name=PushNotificationsRMQOpts.exchange_name,
                exchange_type=ExchangeType.DIRECT,
                queue_durable=True,
                queue_name=PushNotificationsRMQOpts.rk,
            ),
            channel=await self._amqp_conn.get_channel_from_pool(),
            incoming_message_type=SendPushQueueMessage,
            callback=self._handle_message,
            logger=self.logger.bind(subtype="listener"),
        )
        self.logger.debug("Listening for push notifications")

    async def stop(self) -> None:
        await self._updates_listener.stop()
        await self._amqp_conn.stop()
        await self._sender.stop()
        self.logger.debug("Stopped listening for push notifications")

    async def _handle_message(self, update: SendPushQueueMessage) -> None:
        self.logger.debug(f"Received push notification update: {update}")
        update_type = type(update.source_event)
        handler = BaseUpdateHandler.handlers.get(update_type)
        if not handler:
            raise InternalError(f"Handler for {update_type} not found")

        handler_instance = handler(
            logger=self.logger,
            settings=self._settings,
            storage_srvc=self.storage,
        )

        notifications = await handler_instance.handle(update.source_event)

        if not notifications:
            return

        notify_tasks = [self._retrier(self._send_notification, notification) for notification in notifications]

        results = await asyncio.gather(*notify_tasks, return_exceptions=True)
        for result in results:
            if isinstance(result, Exception):
                self.logger.error("Failed to send push notification", exc_info=result)

    async def _send_notification(self, notification: PreparedPushNotification) -> None:
        try:
            await self._sender.send_notification(
                message=notification.content,
                client_credentials=notification.client_credentials,
                ttl=notification.ttl,
                urgency=notification.urgency,
                topic=notification.topic,
            )

        except InvalidEndpointError as exc:
            endpoint = notification.client_credentials.endpoint.geturl()

            self.logger.debug(
                "Invalid endpoint",
                endpoint=endpoint,
                msg=exc.raw_response,
            )
            async with self.storage.connect(autocommit=True) as db:
                await db.push_notifications.remove_configs(device_id=notification.device_id)

        except TryAgainLaterError:
            raise

        except Exception as exc:
            self.logger.critical("Failed to send push notification", exc_info=exc, update_str=repr(notification))
