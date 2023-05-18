from enum import Enum


class Status(str, Enum):
    """
    Поля для статусов
    """
    CURRENT: str = "current"
    COMPLETED: str = "completed"
    FUTURE: str = "future"
