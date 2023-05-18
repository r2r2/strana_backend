from typing import Type

from ..entities import BaseNotificationCase
from ..models import ResponseClientNotificationsSpecsModel
from ..repos import ClientNotificationRepo


class ClientNotificationsSpecsCase(BaseNotificationCase):
    """
    Спеки оповещений.
    """

    def __init__(self, client_notification_repo: Type[ClientNotificationRepo]) -> None:
        self.client_notification_repo: ClientNotificationRepo = client_notification_repo()

    async def __call__(self, *, user_id: int) -> ResponseClientNotificationsSpecsModel:
        specs = await self.client_notification_repo.specs(user_id=user_id)
        return ResponseClientNotificationsSpecsModel(**dict(specs))
