from asyncio import ensure_future, Future, gather
from typing import Type, Any, Union

from ..entities import BaseNotificationCase
from ..types import NotificationPagination
from ..repos import NotificationRepo, Notification


class AgentsNotificationsListCase(BaseNotificationCase):
    """
    Список уведомлений агента
    """

    def __init__(self, notification_repo: Type[NotificationRepo]) -> None:
        self.notification_repo: NotificationRepo = notification_repo()

    async def __call__(self, agent_id: int, pagination: NotificationPagination) -> dict[str, Any]:
        filters: dict[str, Any] = dict(user_id=agent_id)
        notifications: list[Notification] = await self.notification_repo.list(
            filters=filters, end=pagination.end, start=pagination.start
        )
        counted: list[tuple[Union[int, str]]] = await self.notification_repo.count(filters=filters)
        futures: list[Future] = list()
        for notification in notifications:
            if not notification.is_sent:
                data: dict[str, Any] = dict(is_sent=True)
                futures.append(
                    ensure_future(
                        self.notification_repo.update(notification, data=data)
                    )
                )
        count: int = len(counted)
        if count and count == 1:
            count: int = counted[0][0]
        data: dict[str, Any] = dict(
            count=count, page_info=pagination(count=count), result=notifications
        )
        await gather(*futures)
        return data
