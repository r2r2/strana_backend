from typing import Optional

from pydantic import EmailStr

from ..entities import BaseUserModel


class RequestProcessLoginModel(BaseUserModel):
    """
    Модель запроса на вход
    """

    email: EmailStr
    password: str

    class Config:
        orm_mode = True


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
