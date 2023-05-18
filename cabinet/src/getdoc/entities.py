from pydantic import BaseModel

from common.orm.entities import BaseRepo


class BaseTemplateModel(BaseModel):
    """
    Базовая модель шаблонов
    """

class BaseTemplateRepo(BaseRepo):
    """
    Базовый репозиторий шаблонов
    """


class BaseTemplateException(Exception):
    """
    Базовая ошибка шаблонов
    """

    message: str
    status: int
    reason: str
