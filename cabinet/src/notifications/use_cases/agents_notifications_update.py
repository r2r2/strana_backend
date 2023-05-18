from pytz import UTC
from datetime import datetime
from typing import Type, Any


from ..entities import BaseNotificationCase
from ..exceptions import NotificationNotFoundError
from ..repos import NotificationRepo, Notification
from ..models import RequestAgentsNotificationsUpdateModel


class AgentsNotificationsUpdateCase(BaseNotificationCase):
    """
    Обновление уведомления агента
    """

    def __init__(self, notification_repo: Type[NotificationRepo]) -> None:
        self.notification_repo: NotificationRepo = notification_repo()

    async def __call__(
        self, agent_id: int, notification_id: int, payload: RequestAgentsNotificationsUpdateModel
    ) -> Notification:
        data: dict[str, Any] = payload.dict()
        filters: dict[str, Any] = dict(user_id=agent_id, id=notification_id)
        notification: Notification = await self.notification_repo.retrieve(filters=filters)
        if not notification:
            raise NotificationNotFoundError
        data["read"]: datetime = datetime.now(tz=UTC)
        notification: Notification = await self.notification_repo.update(notification, data=data)
        return notification
