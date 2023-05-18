from typing import Any

from ..entities import BaseUserModel


class RequestRepresesUsersSpecsModel(BaseUserModel):
    """
    Модель запроса спеков пользователей представителей агенства
    """

    class Config:
        orm_mode = True


class ResponseRepresesUsersSpecsModel(BaseUserModel):
    """
    Модель ответа спеков пользователей представителей агенства
    """

    specs: dict[str, Any]
    ordering: list[Any]

    class Config:
        orm_mode = True
