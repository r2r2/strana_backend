from datetime import datetime
from typing import Optional

from src.notifications.entities import BaseNotificationModel


class RequestAgentsNotificationStreamModel(BaseNotificationModel):
    """
    Модель запроса стриминга уведомлений агентов
    """

    id: int
    is_read: bool

    class Config:
        orm_mode = True


class ResponseAgentsNotificationStreamModel(BaseNotificationModel):
    """
    Модель ответа стриминга уведомлений агентов
    """

    id: int
    is_read: bool
    is_sent: bool
    message: Optional[str]
    sent: Optional[datetime]
    read: Optional[datetime]

    class Config:
        orm_mode = True
