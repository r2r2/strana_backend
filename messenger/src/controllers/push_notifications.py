import secrets

from fastapi import Depends, HTTPException, status
from py_vapid import Vapid
from sl_messenger_protobuf.messages_pb2 import MessageContent
from web_pusher import WebPusherClient

from src.core.di import Injected
from src.core.logger import get_logger
from src.entities.push_notifications import PushClientCredentials
from src.modules.push_notifications import PushNotificationsVapidSettings
from src.modules.storage.dependencies import inject_storage
from src.modules.storage.interface.storage import StorageProtocol
from src.modules.storage.models import PushNotificationConfig


class PushNotificationsController:
    def __init__(
        self,
        vapid_settings: PushNotificationsVapidSettings = Injected[PushNotificationsVapidSettings],
        storage: StorageProtocol = Depends(inject_storage),
    ) -> None:
        self.logger = get_logger()
        self._storage = storage
        self._vapid_settings = vapid_settings

    @staticmethod
    def _generate_device_id() -> str:
        return secrets.token_urlsafe(75)  # 100 chars

    def get_public_key(self) -> str:
        return WebPusherClient.get_vapid_public_key(
            vapid=Vapid.from_pem(self._vapid_settings.private_key.get_secret_value().encode("utf8"))
        )

    async def recover_device_id(self, user_id: int, endpoint: str) -> str:
        result = await self._storage.push_notifications.get_config_by_endpoint(endpoint=endpoint, user_id=user_id)
        if not result:
            raise HTTPException(status.HTTP_422_UNPROCESSABLE_ENTITY, "Subscription not found")

        return result.device_id

    async def on_device_alive(self, user_id: int, device_id: str) -> None:
        push_cfg = await self._storage.push_notifications.get_and_mark_as_alive(device_id=device_id)
        if not push_cfg:
            self.logger.warning("Device not found in the database", param_value_int=device_id)
            return

        if push_cfg.user_id != user_id:
            # Other user logged in with the same device, remove the subscription
            await self.remove_subscriptions(device_id=device_id)
            await self._storage.commit_transaction()

            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Conflict: device is linked to another user",
            )

    async def add_subscription(self, user_id: int, credentials: PushClientCredentials) -> PushNotificationConfig:
        if not (
            config := await self._storage.push_notifications.add_config(
                user_id=user_id,
                device_id=self._generate_device_id(),
                credentials=credentials,
            )
        ):
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Subscription already exists",
            )

        return config

    async def remove_subscriptions(self, device_id: str) -> None:
        if not await self._storage.push_notifications.remove_configs(device_id=device_id):
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Subscriptions not found",
            )

    @staticmethod
    def extract_referenced_user_ids_from_content(content: MessageContent) -> list[int]:
        ctype = content.WhichOneof("content")
        match ctype:
            case "chat_created_notification":
                return [content.chat_created_notification.created_by_user_id]

            case "user_joined_chat_notification":
                return [content.user_joined_chat_notification.user_id]

            case "ticket_closed_notification":
                return [content.ticket_closed_notification.closed_by_user_id]

            case "user_left_chat_notification":
                return [content.user_left_chat_notification.user_id]

            case _:
                return []
