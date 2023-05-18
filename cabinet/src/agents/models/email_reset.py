from pydantic import EmailStr
from ..entities import BaseAgentModel


class RequestEmailResetModel(BaseAgentModel):
    """
    Модель запроса письма сброса пароля
    """

    email: EmailStr

    class Config:
        orm_mode = True


class ResponseEmailResetModel(BaseAgentModel):
    """
    Модель ответа письма сброса пароля
    """

    id: int

    class Config:
        orm_mode = True
