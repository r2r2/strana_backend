from typing import Type, Optional

from ..entities import BaseNotificationCase
from ..models import ResponseClientNotificationsModel
from ..repos import ClientNotificationRepo


class ClientNotificationsListCase(BaseNotificationCase):
    """
    Список оповещений клиента
    """

    def __init__(self, client_notification_repo: Type[ClientNotificationRepo]) -> None:
        self.client_notification_repo: ClientNotificationRepo = client_notification_repo()

    async def __call__(
        self, user_id: int, limit: int, offset: int
    ) -> ResponseClientNotificationsModel:
        notifications, next_page = await self.client_notification_repo.list(
            user_id=user_id, limit=limit, offset=offset
        )
        await self.client_notification_repo.set_new(
            is_new=False, user_id=user_id, ids=[notification.id for notification in notifications]
        )
        return ResponseClientNotificationsModel(next_page=next_page, results=notifications)
