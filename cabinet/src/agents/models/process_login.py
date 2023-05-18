from typing import Optional

from pydantic import EmailStr

from ..entities import BaseAgentModel


class RequestProcessLoginModel(BaseAgentModel):
    """
    Модель запроса на вход
    """

    email: EmailStr
    password: str

    class Config:
        orm_mode = True


class ResponseProcessLoginModel(BaseAgentModel):
    """
    Модель ответа на вход
    """
    id: int
    role: Optional[str]
    type: Optional[str]
    token: Optional[str]

    class Config:
        orm_mode = True
