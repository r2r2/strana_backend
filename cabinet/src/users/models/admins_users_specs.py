from typing import Any

from ..entities import BaseUserModel


class RequestAdminsUsersSpecsModel(BaseUserModel):
    """
    Модель запроса спеков пользователей администратором
    """

    class Config:
        orm_mode = True


class ResponseAdminsUsersSpecsModel(BaseUserModel):
    """
    Модель ответа спеков пользователей администратором
    """

    specs: dict[str, Any]
    ordering: list[Any]

    class Config:
        orm_mode = True
