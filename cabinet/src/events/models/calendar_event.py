from datetime import datetime
from typing import Any, Optional
from pydantic import Field

from ..entities import BaseEventModel
from ..repos import CalendarEventType, CalendarEventFormatType
from pydantic import root_validator


class ResponseCalendarEventModel(BaseEventModel):
    """
    Модель событий календаря для списка.
    """
    id: int
    title: Optional[str]
    type: Optional[CalendarEventType.serializer]
    format_type: Optional[CalendarEventFormatType.serializer]
    date_start: Optional[datetime]
    date_end: Optional[datetime]
    event_id: Optional[int]
    meeting_id: Optional[int]
    background_color: Optional[str]
    tags: Optional[Any]

    # Method fields
    type_id: Optional[int] = Field(None, alias="typeId")

    @root_validator
    def get_calendar_info(cls, values: dict[str, Any]) -> dict[str, Any]:
        """
        Получение информации по тегам события календаря.
        """
        tags: Any = values.pop("tags", None)
        event_id = values.pop("event_id", None)
        meeting_id = values.pop("meeting_id", None)

        type_id = event_id if event_id else meeting_id
        values["type_id"]: Optional[int] = type_id

        event_tags = []
        for tag in tags:
            event_tags.append(dict(
                name=tag.label,
                color=tag.color,
                textСolor=tag.background_color,
            ))
        values["tags"]: list[dict[str, str]] = event_tags

        return values

    class Config:
        orm_mode = True
        allow_population_by_field_name = True

        @staticmethod
        def schema_extra(schema: dict[str, Any]) -> None:
            schema["properties"].pop("eventId")
            schema["properties"].pop("meetingId")


class ResponseListCalendarEventModel(BaseEventModel):
    count: int
    record_count: int
    result: list[ResponseCalendarEventModel]

    class Config:
        orm_mode = True
