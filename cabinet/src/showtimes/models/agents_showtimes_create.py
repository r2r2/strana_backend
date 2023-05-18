from datetime import datetime
from typing import Any, Optional
from pydantic import constr, validator

from common.utils import parse_phone
from src.properties import constants as properties_constants

from ..exceptions import ShowtimeIncorrectPhoneFormatError
from ..entities import BaseShowTimeModel


class RequestAgentsShowtimesCreateModel(BaseShowTimeModel):
    """
    Модель запроса создания записи на показ агентом
    """

    phone: str
    visit: datetime
    name: constr(max_length=50)

    project_id: Optional[int]
    property_type: Optional[properties_constants.PropertyTypes.validator]

    @validator("phone")
    def validate_phone(cls, phone: str) -> str:
        phone: Optional[str] = parse_phone(phone)
        if phone is None:
            raise ShowtimeIncorrectPhoneFormatError
        return phone

    class Config:
        orm_mode = True


class ResponseAgentsShowtimesCreateModel(BaseShowTimeModel):
    """
    Модель ответа создания записи на показ агентом
    """

    class Config:
        orm_mode = True
