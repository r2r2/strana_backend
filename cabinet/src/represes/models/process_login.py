from typing import Optional

from pydantic import EmailStr

from ..entities import BaseRepresModel


class RequestProcessLoginModel(BaseRepresModel):
    """
    Модель запроса на вход
    """

    email: EmailStr
    password: str

    class Config:
        orm_mode = True


class ResponseProcessLoginModel(BaseRepresModel):
    """
    Модель ответа на вход
    """

    id: int
    role: Optional[str]
    type: Optional[str]
    token: Optional[str]

    class Config:
        orm_mode = True
