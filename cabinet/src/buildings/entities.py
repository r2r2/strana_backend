from typing import Any

from pydantic import BaseModel

from common.orm.entities import BaseRepo


class BasBuildingModel(BaseModel):
    """
    Базовая модель корпуса
    """


class BaseBuildingRepo(BaseRepo):
    """
    Базовый репозиторий корпуса
    """


class BaseBuildingCase(object):
    """
    Базовый сценарий корпуса
    """

    async def __call__(self, *args, **kwargs) -> Any:
        raise NotImplementedError
