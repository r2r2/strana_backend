import base64
import time

from sl_messenger_protobuf.notifications_pb2 import PushNotificationContent
from web_pusher import ClientCredentials, WebPusherClient
from web_pusher.enums import Urgency
from web_pusher.exceptions import (
    BadRequestError,
    ForbiddenError,
    InternalServerError,
    InvalidEndpointError,
    PayloadTooLargeError,
    TryAgainLaterError,
    UnauthorizedError,
    WebPushError,
)

from src.core.logger import LoggerName, get_logger

from .interface import PushNotificationsSenderProto
from .settings import PushNotificationsSenderSettings


class PushNotificationsSender(PushNotificationsSenderProto):
    def __init__(
        self,
        settings: PushNotificationsSenderSettings,
    ) -> None:
        self._settings = settings
        self._client = WebPusherClient(
            valid_private_key=settings.vapid.private_key.get_secret_value(),
            vapid_jwt_ttl=settings.vapid.token_ttl,
            vapid_email=settings.vapid.email,
            send_push_request_timeout=settings.send_push_request_timeout,
        )
        self._logger = get_logger(LoggerName.PUSH_SENDER)

    async def start(self) -> None:
        self._logger.debug("Starting push notifications service")

    async def stop(self) -> None:
        await self._client.close()
        self._logger.debug("Stopped push notifications service")

    async def send_notification(
        self,
        *,
        message: PushNotificationContent,
        client_credentials: ClientCredentials,
        ttl: int,
        urgency: Urgency,
        topic: str | None = None,
    ) -> None:
        """Send push notification

        Args:
            message (PushNotificationContent): message to send
            client_credentials (ClientCredentials): recipient credentials
            ttl (int): time to live
            urgency (Urgency): urgency
            topic (str | None, optional): topic to send to. Defaults to None.

        Raises:
            InvalidEndpointError: invalid endpoint
            TryAgainLaterError: try again later
        """
        serialized_msg = base64.b64encode(message.SerializeToString())

        self._logger.debug(
            "Sending push notification",
            extra={
                "message_content_type": message.WhichOneof("content"),
                "endpoint": client_credentials.endpoint.geturl(),
                "ttl": ttl,
                "urgency": urgency,
                "topic": topic,
            },
        )

        tstart = time.perf_counter()
        try:
            await self._client.send_push(
                recipient=client_credentials,
                payload=serialized_msg,
                ttl=ttl,
                urgency=urgency,
                topic=topic,
            )

        except BadRequestError as exc:
            self._logger.warning(
                "Push send failed",
                reason="bad request",
                msg=exc.msg,
                exc_info=exc,
            )
            return

        except ForbiddenError as exc:
            self._logger.warning(
                "Push send failed",
                reason="forbidden",
                msg=exc.msg,
                exc_info=exc,
            )
            return

        except (UnauthorizedError, InternalServerError) as exc:
            self._logger.warning(
                "Push send failed",
                reason="unauthorized or internal server error",
                msg=exc.msg,
                exc_info=exc,
            )
            return

        except (InvalidEndpointError, TryAgainLaterError):
            raise

        except PayloadTooLargeError as exc:
            self._logger.critical(
                "Push send failed",
                reason="payload too large",
                msg=exc.msg,
                exc_info=exc,
            )
            return

        except WebPushError as exc:
            self._logger.warning(
                "Push send failed",
                reason="unexpected error",
                msg=exc.msg,
                exc_info=exc,
            )
            return

        tend = time.perf_counter()
        self._logger.debug("Push send succeeded", param_value_float=round(tend - tstart, 3))
