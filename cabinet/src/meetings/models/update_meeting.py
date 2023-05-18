from datetime import datetime
from typing import Optional

from src.meetings.entities import BaseMeetingModel
from .create_meeting import ResponseCreatedMeetingModel


class RequestUpdateMeetingModel(BaseMeetingModel):
    """
    Модель изменения встречи
    """
    city_id: Optional[int]
    project_id: Optional[int]
    type: Optional[str]
    topic: Optional[str]
    date: Optional[datetime]


class ResponseUpdateMeetingModel(ResponseCreatedMeetingModel):
    """
    Модель ответа изменения встречи
    """
