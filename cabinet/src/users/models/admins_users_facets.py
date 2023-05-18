from typing import Any

from ..entities import BaseUserModel


class RequestAdminsUsersFacetsModel(BaseUserModel):
    """
    Модель запроса фасетов пользователей администратором
    """

    class Config:
        orm_mode = True


class ResponseAdminsUsersFacetsModel(BaseUserModel):
    """
    Модель ответа фасетов пользователей администратором
    """

    count: int
    facets: dict[str, Any]

    class Config:
        orm_mode = True
