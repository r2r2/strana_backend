from typing import Any

from pydantic import BaseModel

from common.orm.entities import BaseRepo


class BaseCautionModel(BaseModel):
    """
    Базовая модель предупреждения
    """


class BaseCautionRepo(BaseRepo):
    """
    Базовый репозиторий предупреждений
    """


class BaseCautionService(object):
    """
    Базовый сервис предупреждений
    """

    async def __call__(self, *args: list[Any], **kwargs: dict[str, Any]) -> Any:
        raise NotImplementedError


class BaseCautionCase(object):
    """
    Базовый сценарий предупреждения
    """

    async def __call__(self, *args: list[Any], **kwargs: dict[str, Any]) -> Any:
        raise NotImplementedError


class BaseCautionException(Exception):
    """
    Базовая ошибка предупреждения
    """

    message: str
    status: int
    reason: str
