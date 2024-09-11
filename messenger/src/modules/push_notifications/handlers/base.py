from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any, Generic, Type, TypeVar

from sl_messenger_protobuf.notifications_pb2 import PushNotificationContent
from web_pusher import ClientCredentials
from web_pusher.enums import Urgency

from src.core.types import LoggerType
from src.modules.push_notifications import PushNotificationsListenerSettings
from src.modules.push_notifications.interface import SourceEventType
from src.modules.storage import StorageServiceProto
from src.modules.storage.interface import StorageProtocol
from src.modules.storage.models import PushNotificationConfig
from src.providers.time import datetime_now

SourceEventTypeT = TypeVar("SourceEventTypeT", bound=SourceEventType)


@dataclass(repr=True, kw_only=True)
class PreparedPushNotification:
    recipient_user_id: int
    content: PushNotificationContent
    client_credentials: ClientCredentials = field(repr=False)
    device_id: str
    ttl: int
    urgency: Urgency = Urgency.HIGH
    topic: str | None = None


class BaseUpdateHandler(ABC, Generic[SourceEventTypeT]):
    handlers: "dict[Type[SourceEventType], Type[BaseUpdateHandler[SourceEventType]]]" = {}
    message_type: Type[SourceEventTypeT]

    def __init__(
        self,
        logger: LoggerType,
        settings: PushNotificationsListenerSettings,
        storage_srvc: StorageServiceProto,
    ) -> None:
        self.logger = logger.bind(handler=self.__class__.__name__)
        self.settings = settings
        self.storage_srvc = storage_srvc

    def __init_subclass__(
        cls: "Type[BaseUpdateHandler[SourceEventTypeT]]",
        update_type: Type[SourceEventTypeT],
        **kwargs: Any,
    ) -> None:
        super().__init_subclass__(**kwargs)
        BaseUpdateHandler.handlers[update_type] = cls
        cls.message_type = update_type

    @abstractmethod
    async def handle(self, update: SourceEventTypeT) -> list[PreparedPushNotification]: ...

    def _truncate_message(self, message: PushNotificationContent) -> None:
        preview_length = self.settings.message_preview_length

        match message.WhichOneof("content"):
            case "new_message":
                content = message.new_message.content
                if content.WhichOneof("content") == "text" and len(content.text.text) > preview_length:
                    content.text.text = content.text.text[: preview_length - 3] + "..."

            case _:
                ...

    @staticmethod
    def _anonymize_message(message: PushNotificationContent) -> None:
        ctype = message.WhichOneof("content")
        match ctype:
            case "new_message":
                for recipient in message.new_message.user_data:
                    recipient.ClearField("name")

            case _:
                return

    async def get_active_configs_for_user(self, db: StorageProtocol, user_id: int) -> list[PushNotificationConfig]:
        push_configs = await db.push_notifications.get_configs_for_user(user_id=user_id)
        if not push_configs:
            return []

        results = []

        for config in push_configs:
            last_alive_at = config.last_alive_at
            now = datetime_now()
            if now - self.settings.device_last_alive_threshold > last_alive_at:
                await db.push_notifications.remove_configs(device_id=config.device_id)
                self.logger.debug(
                    "Push cfg invalidated (last_alive_at)",
                    device_id=config.device_id,
                )
            else:
                results.append(config)

        return results
