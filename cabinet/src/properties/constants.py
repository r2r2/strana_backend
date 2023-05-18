from common import mixins


class PropertyStatuses(mixins.Choices):
    """
    Статусы объектов недвижимости
    """

    FREE = 0, "Свободно"
    SOLD = 1, "Продано"
    BOOKED = 2, "Забронировано"


class PropertyTypes(mixins.Choices):
    """
    Типы объектов недвижимости
    """

    FLAT: str = "FLAT", "Квартира"
    PARKING: str = "PARKING", "Паркинг"
    COMMERCIAL: str = "COMMERCIAL", "Коммерция"
    PANTRY: str = "PANTRY", "Кладовка"
    COMMERCIAL_APARTMENT: str = "COMMERCIAL_APARTMENT", "Апартаменты коммерции"


class PremiseType(mixins.Choices):
    """
    Тип дома объекта недвижимости
    """

    NONRESIDENTIAL: str = "NONRESIDENTIAL", "Нежилое помещение"
    RESIDENTIAL: str = "RESIDENTIAL", "Многоквартирный жилой дом"
