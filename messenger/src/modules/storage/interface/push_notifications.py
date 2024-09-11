from typing import Protocol

from src.entities.push_notifications import PushClientCredentials
from src.modules.storage.models.push_notification import PushNotificationConfig


class PushNotificationConfigsOperationsProtocol(Protocol):
    async def add_config(
        self,
        user_id: int,
        device_id: str,
        credentials: PushClientCredentials,
    ) -> PushNotificationConfig | None: ...

    async def remove_configs(self, device_id: str) -> bool: ...

    async def get_configs_for_user(self, user_id: int) -> list[PushNotificationConfig]: ...

    async def invalidate_configs(self, user_id: int) -> None: ...

    async def get_and_mark_as_alive(self, device_id: str) -> PushNotificationConfig | None: ...

    async def get_config_by_endpoint(self, endpoint: str, user_id: int) -> PushNotificationConfig | None: ...
