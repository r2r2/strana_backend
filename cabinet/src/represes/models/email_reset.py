from pydantic import EmailStr
from ..entities import BaseRepresModel


class RequestEmailResetModel(BaseRepresModel):
    """
    Модель запроса письма сброса пароля
    """

    email: EmailStr

    class Config:
        orm_mode = True


class ResponseEmailResetModel(BaseRepresModel):
    """
    Модель ответа письма сброса пароля
    """

    id: int

    class Config:
        orm_mode = True
