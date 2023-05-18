from typing import Any

from pydantic import BaseModel

from common.orm.entities import BaseRepo


class BasePropertyModel(BaseModel):
    """
    Базовая модель объекта недвижимости
    """


class BasePropertyRepo(BaseRepo):
    """
    Базовый репозиторий объекта невдижимости
    """


class BasePropertyCase(object):
    """
    Базовый сценарий объекта недвижимости
    """

    async def __call__(self, *args: list[Any], **kwargs: dict[str, Any]) -> Any:
        raise NotImplementedError


class BasePropertyService(object):
    """
    Базовый сервис объекта недвижимости
    """

    async def __call__(self, *args: list[Any], **kwargs: dict[str, Any]) -> Any:
        raise NotImplementedError


class BasePropertyException(Exception):
    """
    Базовая ошибка объекта недвижимости
    """

    message: str
    status: int
    reason: str
