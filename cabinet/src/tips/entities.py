from typing import Any

from pydantic import BaseModel

from common.orm.entities import BaseRepo


class BaseTipModel(BaseModel):
    """
    Базовая модель подсказки
    """


class BaseTipRepo(BaseRepo):
    """
    Базовый репозиторий подсказки
    """


class BaseTipCase(object):
    """
    Базовый сценарий подсказки
    """

    async def __call__(self, *args, **kwargs) -> Any:
        raise NotImplementedError
