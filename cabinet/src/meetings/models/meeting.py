from datetime import datetime
from typing import Optional, Any
from pydantic import validator, Field

from src.agents.models import AgentRetrieveModel
from src.agencies.models import AgencyRetrieveModel
from ..entities import BaseMeetingModel
from ..constants import MeetingTopicType, MeetingPropertyType, MeetingType


class BookingMeetingModel(BaseMeetingModel):
    """
    Модель бронирования
    """

    id: int
    amocrm_id: int
    agent: Optional[AgentRetrieveModel]
    agency: Optional[AgencyRetrieveModel]

    class Config:
        orm_mode = True


class ResponseStatusMeetingModel(BaseMeetingModel):
    """
    Модель бронирования
    """

    slug: str = Field(..., alias="value")
    label: str

    class Config:
        orm_mode = True
        allow_population_by_field_name = True


class ResponseMeetingModel(BaseMeetingModel):
    """
    Модель встречи
    """
    id: int
    city_id: int
    project_id: Optional[int]
    booking: Optional[BookingMeetingModel]
    status: ResponseStatusMeetingModel
    record_link: Optional[str]
    meeting_link: Optional[str]
    meeting_address: Optional[str]
    topic: MeetingTopicType.serializer
    type: MeetingType.serializer
    property_type: MeetingPropertyType.serializer
    date: datetime

    class Config:
        orm_mode = True

    @validator('date')
    def validate_date(cls, date: datetime) -> str:
        return date.strftime("%Y-%m-%dT%H:%M")


class ResponseMeetingsListModel(BaseMeetingModel):
    """
    Модель ответа списка встреч
    """
    count: int
    page_info: dict[str, Any]
    result: list[ResponseMeetingModel]
