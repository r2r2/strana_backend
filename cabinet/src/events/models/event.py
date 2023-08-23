from datetime import datetime
from typing import Any, Optional

from ..entities import BaseEventModel
from ..repos import EventType
from pydantic import root_validator, Field


class CityModel(BaseEventModel):
    """
    Модель города мероприятия.
    """
    id: int
    name: str
    slug: str

    class Config:
        orm_mode = True


class ResponseEventModel(BaseEventModel):
    """
    Модель мероприятия.
    """
    id: int
    name: str
    description: Optional[str]
    comment: Optional[str]
    type: Optional[EventType.serializer]
    city: Optional[CityModel]
    address: Optional[str]
    link: Optional[str]
    image: Optional[dict[str, Any]]
    meeting_date_start: Optional[datetime] = Field(None, alias="dateStart")
    meeting_date_end: Optional[datetime] = Field(None, alias="dateEnd")
    record_date_end: Optional[datetime]
    manager_fio: str = Field(..., alias="managerFullName")
    manager_phone: str
    max_participants_number: int = Field(..., alias="maxParticipantsCount")
    participants_count: int
    agent_recorded: bool = Field(..., alias="isParticipant")

    # Method fields
    has_empty_seats: Optional[bool]

    @root_validator
    def get_maintainer_info(cls, values: dict[str, Any]) -> dict[str, Any]:
        """
        Получение информации представителя агенства
        """
        max_participants_number: int = values.get("max_participants_number", 0)
        participants_count: int = values.get("participants_count", 0)

        if not max_participants_number:
            values["has_empty_seats"]: bool = True
        else:
            if participants_count < max_participants_number:
                values["has_empty_seats"]: bool = True
            else:
                values["has_empty_seats"]: bool = False

        return values

    class Config:
        orm_mode = True
        allow_population_by_field_name = True


class ResponseEventListModel(BaseEventModel):
    """
    Модель мероприятия для списка.
    """
    id: int
    name: str
    type: Optional[EventType.serializer]
    meeting_date_start: Optional[datetime] = Field(None, alias="dateStart")
    meeting_date_end: Optional[datetime] = Field(None, alias="dateEnd")
    max_participants_number: int
    participants_count: int
    agent_recorded: bool = Field(..., alias="isParticipant")

    # Method fields
    has_empty_seats: Optional[bool]

    @root_validator
    def get_maintainer_info(cls, values: dict[str, Any]) -> dict[str, Any]:
        """
        Получение информации представителя агенства
        """
        max_participants_number: int = values.pop("max_participants_number", 0)
        participants_count: int = values.pop("participants_count", 0)

        if not max_participants_number:
            values["has_empty_seats"]: bool = True
        else:
            if participants_count < max_participants_number:
                values["has_empty_seats"]: bool = True
            else:
                values["has_empty_seats"]: bool = False

        return values

    class Config:
        orm_mode = True
        allow_population_by_field_name = True

        @staticmethod
        def schema_extra(schema: dict[str, Any]) -> None:
            schema["properties"].pop("maxParticipantsNumber")
            schema["properties"].pop("participantsCount")


class ResponseListEventModel(BaseEventModel):
    count: int
    record_count: int
    result: list[ResponseEventListModel]

    class Config:
        orm_mode = True
