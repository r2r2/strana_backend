from typing import Any, Optional

from pydantic import validator

from src.agencies import constants as agencies_constants

from ..entities import BaseAgentModel


class RequestAdminsAgentsListModel(BaseAgentModel):
    """
    Модель запроса списка агентов администратором
    """

    class Config:
        orm_mode = True


class _AgencyRetrieveModel(BaseAgentModel):
    """
    Модель детального агенства
    """

    id: int
    inn: Optional[str]
    city: Optional[str]
    name: Optional[str]
    type: Optional[agencies_constants.AgencyType.serializer]

    @validator("city", pre=True)
    def get_city_name(cls, value):
        if value:
            return value.name
        return None

    class Config:
        orm_mode = True


class _AgentListModel(BaseAgentModel):
    """
    Модель агента в списке
    """

    id: int
    is_approved: bool
    name: Optional[str]
    phone: Optional[str]
    email: Optional[str]
    surname: Optional[str]
    patronymic: Optional[str]
    active_clients: Optional[int]
    succeed_clients: Optional[int]

    agency: Optional[_AgencyRetrieveModel]

    class Config:
        orm_mode = True


class ResponseAdminsAgentsListModel(BaseAgentModel):
    """
    Модель ответа списка агентов администратором
    """

    count: int
    page_info: dict[str, Any]
    result: list[_AgentListModel]

    class Config:
        orm_mode = True
