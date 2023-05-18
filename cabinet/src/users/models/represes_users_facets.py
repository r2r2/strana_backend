from typing import Any

from ..entities import BaseUserModel


class RequestRepresesUsersFacetsModel(BaseUserModel):
    """
    Модель запроса фасетов пользователей представителей агенства
    """

    class Config:
        orm_mode = True


class ResponseRepresesUsersFacetsModel(BaseUserModel):
    """
    Модель ответа фасетов пользователей представителей агенства
    """

    count: int
    facets: dict[str, Any]

    class Config:
        orm_mode = True
