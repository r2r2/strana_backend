from typing import Any

from pydantic import BaseModel

from common.orm.entities import BaseRepo


class BaseAdminModel(BaseModel):
    """
    Базовая модель администратора
    """


class BaseAdminRepo(BaseRepo):
    """
    Базовый репозиторий администратора
    """


class BaseAdminCase(object):
    """
    Базовый сценарий администратора
    """

    async def __call__(self, *args: Any, **kwargs: Any) -> Any:
        raise NotImplementedError


class BaseAdminException(Exception):
    """
    Базовая ошибка администратора
    """

    message: str
    status: int
    reason: str
