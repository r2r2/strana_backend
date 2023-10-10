from common.orm.entities import BaseRepo
from common.pydantic import CamelCaseBaseModel


class BaseEventListModel(CamelCaseBaseModel):
    """
    Базовая модель мероприятий
    """
    class Config:
        orm_mode = True


class BaseEventListRepo(BaseRepo):
    """
    Базовый репозиторий мероприятий
    """


class BaseEventListCase:
    """
    Базовый сценарий мероприятий
    """


class BaseEventListService:
    """
    Базовый сервис мероприятий
    """


class BaseEventListException(Exception):
    """
    Базовая ошибка для мероприятий
    """
    message: str
    status: int
    reason: str
