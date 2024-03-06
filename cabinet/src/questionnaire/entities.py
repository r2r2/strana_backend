from typing import Any

from tortoise import Model

from common.orm.entities import BaseRepo
from common.models import TimeBasedMixin


class BaseQuestionnaireRepo(BaseRepo):
    """
    Базовый репозиторий опросника
    """

    async def __call__(self, *args: list[Any], **kwargs: dict[str, Any]) -> Any:
        raise NotImplementedError


class BaseQuestionnaireModel(Model, TimeBasedMixin):
    """
    Базовая модель опросника
    """


class BaseQuestionnaireCase:
    """
    Базовый сценарий объекта недвижимости
    """

    async def __call__(self, *args: list[Any], **kwargs: dict[str, Any]) -> Any:
        raise NotImplementedError


class BaseQuestionnaireException(Exception):
    """
    Базовая ошибка заявки на ипотеку
    """

    message: str
    status: int
    reason: str
