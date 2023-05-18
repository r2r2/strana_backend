from typing import Optional
from datetime import datetime

from ..entities import BaseNotificationModel


class RequestAgentsNotificationsUpdateModel(BaseNotificationModel):
    """
    Модель запроса списка уведомлений агента
    """

    is_read: bool

    class Config:
        orm_mode = True


class ResponseAgentsNotificationsUpdateModel(BaseNotificationModel):
    """
    Модель ответа списка уведомлений агента
    """

    id: int
    is_read: bool
    is_sent: bool
    message: Optional[str]
    sent: Optional[datetime]
    read: Optional[datetime]

    class Config:
        orm_model = True
