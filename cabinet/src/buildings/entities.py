from typing import Any

from common.orm.entities import BaseRepo
from common.pydantic import CamelCaseBaseModel
from pydantic import BaseModel


class BaseBuildingModel(BaseModel):
    """
    Базовая модель корпуса
    """


class BaseBuildingCamelCaseBaseModel(CamelCaseBaseModel):
    """
    Базовая модель корпуса в CamelCase
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
