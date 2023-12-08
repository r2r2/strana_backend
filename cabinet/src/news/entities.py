from tortoise import Model

from common.orm.entities import BaseRepo
from common.pydantic import CamelCaseBaseModel


class BaseNewsModel(CamelCaseBaseModel):
    """
    Базовая модель новостей.
    """


class BaseNewsDatabaseModel(Model):
    """
    Базовая модель бд новостей.
    """


class BaseNewsRepo(BaseRepo):
    """
    Базовый репозиторий новостей.
    """


class BaseNewsCase:
    """
    Базовый сценарий новостей.
    """


class BaseNewsService:
    """
    Базовый сервис новостей.
    """


class BaseNewsException(Exception):
    """
    Базовая ошибка новостей.
    """

    message: str
    status: int
    reason: str
