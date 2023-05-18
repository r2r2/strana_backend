from common import mixins


class ProjectStatus(mixins.Choices):
    """
    Поля для статусов
    """
    CURRENT: str = "current", "Текущий"
    COMPLETED: str = "completed", "Завершённый"
    FUTURE: str = "future", "Будущий"
