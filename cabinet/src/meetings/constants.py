from common.mixins import Choices

BOOKING_MEETING_STATUSES = [
    "Первичный контакт",
    "Назначить встречу",
    "Фиксация клиента за АН",
    "Встреча назначена",
    "Идет встреча",
    "Принимают решение",
    "Повторная встреча",
]


class MeetingStatusChoice(Choices):
    """
    Статус встречи
    """
    CONFIRM: str = "confirm", "Подтверждена"
    NOT_CONFIRM: str = "not_confirm", "Не подтверждена"
    START: str = "start", "Встреча началась"
    FINISH: str = "finish", "Завершена"
    CANCELLED: str = "cancelled", "Отменена"


class MeetingType(Choices):
    """
    Тип встречи
    """
    ONLINE: str = "kc", "Онлайн"
    OFFLINE: str = "meet", "Офлайн"


class MeetingPropertyType(Choices):
    """
    Тип помещения
    """
    FLAT: str = "flat", "Квартира"
    PARKING: str = "parking", "Паркинг"
    PANTRY: str = "pantry", "Кладовая"
    COMMERCIAL: str = "commercial", "Коммерция"
    APARTMENT: str = "apartment", "Апартаменты"


class MeetingTopicType(Choices):
    """
    Тема встречи
    """
    BUY: str = "buy", "Покупка квартиры"
    MORTGAGE: str = "mortgage", "Ипотека"
