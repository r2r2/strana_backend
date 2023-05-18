from datetime import datetime
from typing import Any, Optional

from ..entities import BaseNotificationModel


class RequestAgentsNotificationsListModel(BaseNotificationModel):
    """
    Модель запроса списка уведомлений агента
    """

    class Config:
        orm_mode = True


class _NotificationListModel(BaseNotificationModel):
    """
    Модель уведомления агента
    """

    id: int
    is_read: bool
    is_sent: bool
    message: Optional[str]
    sent: Optional[datetime]
    read: Optional[datetime]

    class Config:
        orm_mode = True


class ResponseAgentsNotificationsListModel(BaseNotificationModel):
    """
    Модель ответа списка уведомлений агента
    """

    count: int
    page_info: dict[str, Any]
    result: list[_NotificationListModel]

    class Config:
        orm_model = True
