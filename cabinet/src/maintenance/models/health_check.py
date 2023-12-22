from datetime import datetime

from ..entities import BaseMaintenanceModel


class ResponseHealthChecksModel(BaseMaintenanceModel):
    """
    Модель ответа по состоянию сервиса
    """
    city_id: int
    project_id: int | None
    type: str
    topic: str
    date: datetime
    property_type: str
    booking_id: int | None

