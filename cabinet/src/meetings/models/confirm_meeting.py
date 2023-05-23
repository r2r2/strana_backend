from datetime import datetime

from src.meetings.entities import BaseMeetingModel


class RequestConfirmMeetingModel(BaseMeetingModel):
    """
    Модель запроса на подтверждения встречи
    """
    amocrm_id: int
    result: bool
    address: str
    date: datetime
    type: str