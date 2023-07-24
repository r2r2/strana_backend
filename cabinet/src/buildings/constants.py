from enum import Enum

from common import mixins


class BuildingType(mixins.Choices):
    RESIDENTIAL: str = "RESIDENTIAL", "Жилое"
    APARTMENT: str = "APARTMENT", "Апартаменты"
    PARKING: str = "PARKING", "Паркинг"
    OFFICE: str = "OFFICE", "Коммерческое"


class BuildingTypeRequest(str, Enum):
    """
    Типы корпусов для запроса
    """
    RESIDENTIAL: str = "RESIDENTIAL"
    APARTMENT: str = "APARTMENT"
    PARKING: str = "PARKING"
    OFFICE: str = "OFFICE"
