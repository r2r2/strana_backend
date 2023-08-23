from typing import Optional

from pydantic import EmailStr, Field

from ..entities import BaseUserModel, BaseUserCamelCaseModel


class RequestProcessLoginModel(BaseUserModel):
    """
    Модель запроса на вход
    """

    email: EmailStr
    password: str

    class Config:
        orm_mode = True


class RequestSuperuserLoginModel(BaseUserModel):
    """
    Модель запроса на вход суперюзером из админки под выбранным пользователем.
    """

    session_id: str = Field(alias="sessionId")


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
