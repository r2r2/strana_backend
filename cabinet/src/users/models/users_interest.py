from typing import Optional

from src.properties import constants as properties_constants

from ..entities import BaseUserModel
from ..mixins.validators import CleanNoneValidatorMixin


class RequestUsersInterestModel(BaseUserModel, CleanNoneValidatorMixin):
    """
    Модель запроса добавления интересующих объектов пользователю
    """

    interested: Optional[list[int]]
    interested_project: Optional[int]
    interested_type: Optional[properties_constants.PropertyTypes.validator]

    class Config:
        orm_mode = True


class ResponseUsersInterestModel(BaseUserModel):
    """
    Модель ответа добавления интересующих объектов пользователю
    """

    id: int

    class Config:
        orm_mode = True
