from datetime import datetime
from typing import Optional, Any

from ..entities import BaseMeetingModel
from ..constants import MeetingStatus, MeetingTopicType, MeetingPropertyType, MeetingType


class MeetingModel(BaseMeetingModel):
    """
    Модель встречи
    """
    id: int
    city_id: int
    project_id: Optional[int]
    booking_id: Optional[int]
    status: MeetingStatus.serializer
    record_link: Optional[str]
    meeting_link: Optional[str]
    meeting_address: Optional[str]
    topic: MeetingTopicType.serializer
    type: MeetingType.serializer
    property_type: MeetingPropertyType.serializer
    date: datetime


class ResponseMeetingsListModel(BaseMeetingModel):
    """
    Модель ответа списка встреч
    """
    count: int
    page_info: dict[str, Any]
    result: list[MeetingModel]