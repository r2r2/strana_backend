from datetime import datetime
from typing import Optional

from src.meetings.constants import MeetingTopicType, MeetingType, MeetingPropertyType
from src.meetings.entities import BaseMeetingModel
from src.projects.models.projects_list import ProjectListModel
from src.meetings.models import BookingMeetingModel


class RequestCreateMeetingModel(BaseMeetingModel):
    """
    Модель запроса на создание встречи
    """
    city_id: int
    project_id: Optional[int]
    type: str
    topic: str
    date: datetime
    property_type: str
    booking_id: Optional[int]


class _ResponseCity(BaseMeetingModel):
    """
    Модель ответа для города
    """
    name: str
    slug: str


class ResponseCreatedMeetingModel(BaseMeetingModel):
    """
    Модель ответа для создания встречи
    """
    id: int
    city: _ResponseCity
    project: Optional[ProjectListModel]
    booking: Optional[BookingMeetingModel]
    type: MeetingType.serializer
    topic: MeetingTopicType.serializer
    property_type: MeetingPropertyType.serializer
    record_link: Optional[str]
    meeting_link: Optional[str]
    meeting_address: Optional[str]
    date: datetime

    class Config:
        orm_mode = True
