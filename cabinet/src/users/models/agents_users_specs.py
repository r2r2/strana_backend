from typing import Any

from ..entities import BaseUserModel


class RequestAgentsUsersSpecsModel(BaseUserModel):
    """
    Модель запроса спеков пользователей агентов
    """

    class Config:
        orm_mode = True


class ResponseAgentsUsersSpecsModel(BaseUserModel):
    """
    Модель ответа спеков пользователей агентов
    """

    specs: dict[str, Any]
    ordering: list[Any]

    class Config:
        orm_mode = True
