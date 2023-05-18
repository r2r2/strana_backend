from common.mixins import Choices


class MeetingStatus(Choices):
    """
    Статус встречи
    """
    CONFIRM: str = "confirm", "Подтверждена"
    NOT_CONFIRM: str = "not_confirm", "Не подтверждена"
    START: str = "start", "Встреча началась"
    FINISH: str = "finish", "Завершена"


class MeetingType(Choices):
    """
    Тип встречи
    """
    ONLINE: str = "online", "Онлайн"
    OFFLINE: str = "offline", "Офлайн"


class MeetingPropertyType(Choices):
    """
    Тип помещения
    """
    FLAT: str = "flat", "Квартира"


class MeetingTopicType(Choices):
    """
    Тема встречи
    """
    BUY: str = "buy", "Покупка квартиры"
    MORTGAGE: str = "mortgage", "Ипотека"
