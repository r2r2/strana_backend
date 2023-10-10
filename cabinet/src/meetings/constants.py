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
    CONFIRM: tuple[str, str] = "confirm", "Подтверждена"
    NOT_CONFIRM: tuple[str, str] = "not_confirm", "Не подтверждена"
    START: tuple[str, str] = "start", "Встреча началась"
    FINISH: tuple[str, str] = "finish", "Завершена"
    CANCELLED: tuple[str, str] = "cancelled", "Отменена"


class MeetingCreationSourceChoice(Choices):
    """
    Источник создания встречи
    """
    LK_BROKER: tuple[str, str] = "lk_broker", "ЛК Брокера"
    LK_CLIENT: tuple[str, str] = "lk_client", "ЛК Клиента"
    AMOCRM: tuple[str, str] = "amocrm", "Amocrm"


class MeetingType(Choices):
    """
    Тип встречи
    """
    ONLINE: tuple[str, str] = "kc", "Онлайн"
    OFFLINE: tuple[str, str] = "meet", "Офлайн"


class MeetingPropertyType(Choices):
    """
    Тип помещения
    """
    FLAT: tuple[str, str] = "flat", "Квартира"
    PARKING: tuple[str, str] = "parking", "Паркинг"
    PANTRY: tuple[str, str] = "pantry", "Кладовая"
    COMMERCIAL: tuple[str, str] = "commercial", "Коммерция"
    APARTMENT: tuple[str, str] = "apartment", "Апартаменты"


class MeetingTopicType(Choices):
    """
    Тема встречи
    """
    BUY: tuple[str, str] = "buy", "Покупка квартиры"
    MORTGAGE: tuple[str, str] = "mortgage", "Ипотека"
