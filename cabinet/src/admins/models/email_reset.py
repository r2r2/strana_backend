from pydantic import EmailStr
from ..entities import BaseAdminModel


class RequestEmailResetModel(BaseAdminModel):
    """
    Модель запроса письма сброса пароля
    """

    email: EmailStr

    class Config:
        orm_mode = True


class ResponseEmailResetModel(BaseAdminModel):
    """
    Модель ответа письма сброса пароля
    """

    id: int

    class Config:
        orm_mode = True
