from typing import Any

from common.entities import BaseFilter
from common.orm.entities import BaseRepo
from pydantic import BaseModel


class BaseProjectModel(BaseModel):
    """
    Базовая модель проекта
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
