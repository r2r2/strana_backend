from typing import Any

from pydantic import BaseModel

from common.entities import BaseFilter
from common.orm.entities import BaseRepo
from common.pydantic import CamelCaseBaseModel


class BaseProjectModel(BaseModel):
    """
    Базовая модель проекта
    """


class BaseProjectCamelCaseBaseModel(CamelCaseBaseModel):
    """
    Базовая модель проекта в CamelCase
    """


class BaseProjectRepo(BaseRepo):
    """
    Базовый репозиторий проекта
    """


class BaseProjectCase:
    """
    Базовый сценарий проекта
    """

    async def __call__(self, *args, **kwargs) -> Any:
        raise NotImplementedError


class BaseProjectFilter(BaseFilter):
    """
    Базовый фильтр проекта
    """


class BaseProjectException(Exception):
    """
    Базовая ошибка проекта
    """

    message: str
    status: int
    reason: str
