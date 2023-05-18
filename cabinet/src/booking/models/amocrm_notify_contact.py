from datetime import datetime
from typing import Optional

from ..entities import BaseBookingModel


class NotifyContactModel(BaseBookingModel):
    """Модель запроса принятия договора"""

    entity_id: int
    entity_type: int
    is_new_format: int


class RequestNotifyContactModel(BaseBookingModel):
    """Модель запроса оповещения контакта"""

    data: list[NotifyContactModel]
