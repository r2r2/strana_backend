from pydantic import BaseModel
from tortoise import Model

from common.orm.entities import BaseRepo
from common.pydantic import CamelCaseBaseModel


class BaseAdditionalServiceModel(BaseModel):
    """
    Базовая модель дополнительной услуги
    """


class BaseAdditionalServiceDatabaseModel(Model):
    """
    Базовая модель дополнительной услуги
    """


class BaseAdditionalServiceCamelCaseModel(CamelCaseBaseModel):
    """
    Базовая модель дополнительной услуги
    """


class BaseAdditionalServiceRepo(BaseRepo):
    """
    Базовый репозиторий дополнительной услуги
    """


class BaseAdditionalServiceCase:
    """
    Базовый сценарий дополнительной услуги
    """

    async def __call__(self, *args: list, **kwargs: dict):
        raise NotImplementedError


class BaseAdditionalServiceException(Exception):
    """
    Базовая ошибка документа
    """

    message: str
    status: int
    reason: str
