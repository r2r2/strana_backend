from enum import StrEnum


class Status(StrEnum):
    """
    Поля для статусов
    """
    CURRENT: str = "current"
    COMPLETED: str = "completed"
    FUTURE: str = "future"
