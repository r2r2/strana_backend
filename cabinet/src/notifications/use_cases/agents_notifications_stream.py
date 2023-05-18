from pytz import UTC
from datetime import datetime
from typing import Type, Any, AsyncGenerator

from ..entities import BaseNotificationCase
from ..repos import NotificationRepo, Notification
from ..models import ResponseAgentsNotificationStreamModel


class AgentsNotificationStreamCase(BaseNotificationCase):
    """
    Стриминг уведомлений агентов
    """

    def __init__(self, notification_repo: Type[NotificationRepo]) -> None:
        self.notification_repo: NotificationRepo = notification_repo()

    async def __call__(self, agent_id: int) -> AsyncGenerator[AsyncGenerator[dict[str, Any], dict[str, Any]], None]:
        filters: dict[str, Any] = dict(user_id=agent_id, is_sent=False)
        notifications: list[Notification] = await self.notification_repo.list(filters=filters)
        for notification in notifications:
            yield self._streaming(notification=notification)

    async def _streaming(self, notification: Notification) -> AsyncGenerator[dict[str, Any], dict[str, Any]]:
        data: dict[str, Any] = dict(
            is_sent=True,
            sent=datetime.now(tz=UTC)
        )
        y_data: dict[str, Any] = yield ResponseAgentsNotificationStreamModel.from_orm(notification).json()
        id: int = y_data.pop("id")
        if y_data["is_read"]:
            y_data["read"]: datetime = datetime.now(tz=UTC)
        data.update(y_data)
        if notification.id == id:
            await self.notification_repo.update(notification, data=data)



