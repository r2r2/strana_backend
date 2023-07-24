from common import mixins


class ProjectStatus(mixins.Choices):
    """
    Поля для статусов
    """
    CURRENT: str = "current", "Текущий"
    COMPLETED: str = "completed", "Завершённый"
    FUTURE: str = "future", "Будущий"


class ProjectSkyColor(mixins.Choices):
    DARK_BLUE: str = 'dark_blue', 'Синее'
    LIGHT_BLUE: str = 'light_blue', 'Голубое'
    AQUAMARINE: str = 'aquamarine', 'Аквамариновое'
