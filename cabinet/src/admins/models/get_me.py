from typing import Optional
from src.users import constants as users_constants

from ..entities import BaseAdminModel


class RequestGetMeModel(BaseAdminModel):
    """
    Модель запроса получения текущего администратора
    """

    class Config:
        orm_mode = True


class ResponseGetMeModel(BaseAdminModel):
    """
    Модель ответа получения текущего администратора
    """

    is_active: bool
    is_approved: bool
    is_contracted: bool
    name: Optional[str]
    email: Optional[str]
    phone: Optional[str]
    surname: Optional[str]
    patronymic: Optional[str]
    type: Optional[users_constants.UserType.serializer]

    class Config:
        orm_mode = True
