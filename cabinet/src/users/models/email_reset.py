from pydantic import EmailStr
from ..entities import BaseUserModel


class RequestEmailResetModel(BaseUserModel):
    """
    Модель запроса письма сброса пароля
    """

    email: EmailStr

    class Config:
        orm_mode = True


class ResponseEmailResetModel(BaseUserModel):
    """
    Модель ответа письма сброса пароля
    """

    id: int

    class Config:
        orm_mode = True
