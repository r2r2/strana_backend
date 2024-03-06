from typing import Any


from common.orm.entities import BaseRepo
from common.pydantic import CamelCaseBaseModel


class BaseFAQModel(CamelCaseBaseModel):
    """
    Базовая модель FAQ
    """


class BaseFAQRepo(BaseRepo):
    """
    Базовая модель вопросов ЧАВО
    """


class BaseFAQCase(object):
    """
    Базовый сценарий списка вопросов ЧАВО
    """

    async def __call__(self, *args, **kwargs) -> Any:
        raise NotImplementedError
