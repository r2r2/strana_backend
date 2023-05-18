from typing import Any

from pydantic import BaseModel

from common.orm.entities import BaseRepo


class BasFloorModel(BaseModel):
    """
    Базовая модель этажа
    """


class BaseFloorRepo(BaseRepo):
    """
    Базовый репозиторий этажа
    """


class BaseFloorCase(object):
    """
    Базовый сценарий этажа
    """

    async def __call__(self, *args, **kwargs) -> Any:
        raise NotImplementedError
