from typing import Optional

from ..constants import PropertyTypes
from ..entities import BasePropertyModel


class RequestCreatePropertyModel(BasePropertyModel):
    """
    Модель запроса создания объекта недвижимости
    """

    global_id: str
    type: PropertyTypes.validator
    booking_type_id: Optional[int] = None

    class Config:
        orm_mode = True


class ResponseCreatePropertyModel(BasePropertyModel):
    """
    Модель ответа создания объекта недвижимости
    """

    id: int

    class Config:
        orm_mode = True
