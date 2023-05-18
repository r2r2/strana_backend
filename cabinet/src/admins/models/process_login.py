from typing import Optional

from pydantic import EmailStr

from ..entities import BaseAdminModel


class RequestProcessLoginModel(BaseAdminModel):
    """
    Модель запроса на вход
    """

    email: EmailStr
    password: str

    class Config:
        orm_mode = True


class ResponseProcessLoginModel(BaseAdminModel):
    """
    Модель ответа на вход
    """

    id: Optional[int]
    role: Optional[str]
    type: Optional[str]
    token: Optional[str]

    class Config:
        orm_mode = True
