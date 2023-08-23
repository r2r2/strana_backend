from typing import Optional

from pydantic import NoneStr

from src.agencies.constants import AgencyType
from src.agencies.entities import BaseAgencyModel


class RequestAgencyRetrieveModel(BaseAgencyModel):
    """
    Модель запроса получения агенства
    """

    class Config:
        orm_mode = True


class ResponseAgencyRetrieveModel(BaseAgencyModel):
    """
    Модель ответа получения агенства
    """

    id: int
    name: NoneStr
    inn: Optional[str]
    city: Optional[str]
    type: Optional[AgencyType.serializer]

    class Config:
        orm_mode = True
