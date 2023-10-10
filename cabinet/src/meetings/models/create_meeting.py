from datetime import datetime

from src.meetings.constants import MeetingTopicType, MeetingType, MeetingPropertyType
from src.meetings.entities import BaseMeetingModel
from src.meetings.models import BookingMeetingModel
from src.projects.models.projects_list import ProjectListModel


class RequestCreateMeetingModel(BaseMeetingModel):
    """
    Модель запроса на создание встречи
    """
    city_id: int
    project_id: int | None
    type: str
    topic: str
    date: datetime
    property_type: str
    booking_id: int | None


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
    project: ProjectListModel | None
    booking: BookingMeetingModel | None
    type: MeetingType.serializer
    topic: MeetingTopicType.serializer
    property_type: MeetingPropertyType.serializer
    record_link: str | None
    meeting_link: str | None
    meeting_address: str | None
    date: datetime

    class Config:
        orm_mode = True
