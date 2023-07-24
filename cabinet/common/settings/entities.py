from common.orm.entities import BaseRepo


class BaseSettingsRepo(BaseRepo):
    """
    Базовый репозиторий настроек
    """
    pass


class BaseSettingsException(Exception):
    """
    Базовая ошибка настроек
    """
    message: str
    status: int
    reason: str
