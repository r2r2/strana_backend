from common.orm.entities import BaseRepo
from pydantic import BaseModel


class BaseDocTemplateModel(BaseModel):
    """
    Базовая модель шаблонов договоров
    """


class BaseDocTemplateRepo(BaseRepo):
    """
    Базовый репозиторий шаблонов договоров
    """


class BaseDocTemplateException(Exception):
    """
    Базовая ошибка шаблонов договоров
    """

    message: str
    status: int
    reason: str
