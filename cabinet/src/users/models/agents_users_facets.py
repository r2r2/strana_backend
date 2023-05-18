from typing import Any

from ..entities import BaseUserModel


class RequestAgentsUsersFacetsModel(BaseUserModel):
    """
    Модель запроса фасетов пользователей агентов
    """

    class Config:
        orm_mode = True


class ResponseAgentsUsersFacetsModel(BaseUserModel):
    """
    Модель ответа фасетов пользователей агентов
    """

    count: int
    facets: dict[str, Any]

    class Config:
        orm_mode = True
