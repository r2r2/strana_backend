from typing import Optional

from pydantic import EmailStr, Field

from ..entities import BaseUserModel


class RequestProcessLoginModel(BaseUserModel):
    """
    Модель запроса на вход
    """

    email: EmailStr
    password: str
    user_id: int | None = Field(None, alias="userId")

    class Config:
        orm_mode = True
        allow_population_by_field_name = True


class RequestSuperuserClientLoginModel(BaseUserModel):
    """
    Модель запроса на вход суперюзером из админки под выбранным клиентом.
    """
    client_id: int


class ResponseProcessLoginModel(BaseUserModel):
    """
    Модель ответа на выход
    """

    id: Optional[int]
    role: Optional[str]
    type: Optional[str]
    token: Optional[str]
    is_fired: Optional[bool]

    class Config:
        orm_mode = True
