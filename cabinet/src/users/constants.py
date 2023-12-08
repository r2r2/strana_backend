from enum import StrEnum

from common import mixins


class UserType(mixins.Choices):
    """
    Тип пользователя
    """
    ADMIN: str = "admin", "Админ"
    AGENT: str = "agent", "Агент"
    CLIENT: str = "client", "Клиент"
    REPRES: str = "repres", "Представитель"
    MANAGER: str = "manager", "Менеджер"
    ROP: str = "rop", "Руководитель отдела продаж"


class DutyType(mixins.Choices):
    """
    Должность пользователя
    """
    DIRECTOR: str = "director", "Директор"
    BRAND_MANAGER: str = "brand_manager", "Бренд менеджер"
    BUILDING_MANAGER: str = "building_manager", "Менеджер отдела новостроек"
    BUILDING_LEADER: str = "building_leader", "Руководитель отдела новостроек"


class UserStatus(mixins.Choices):
    """
    Статус пользователя
    """

    CHECK: str = "check", "На проверке"
    UNIQUE: str = "unique", "Уникальный"
    REFUSED: str = "refused", "Отказался"
    NOT_UNIQUE: str = "not_unique", "Не уникальный"
    DISPUTE: str = 'dispute', "Оспаривание статуса"
    CAN_DISPUTE: str = 'can_dispute', "Закреплен, но можно оспорить"
    ERROR: str = 'error', "Ошибка"
    SAME_PINNED: str = 'same_pinned', "Закреплен за вами"
    AGENT_REPRES_PINNED: str = 'agent_repres_pinned', "Закреплен за агентом из вашего агентства"
    REPRES_PINNED_DISPUTE: str = 'repres_pinned_dispute', 'Закреплен за вашим агентством, но можно оспорить'


class UserStatusCheck(mixins.Choices):
    """
    Статус проверки пользователя
    """

    UNIQUE: str = "unique", "Уникальный"
    NOT_UNIQUE: str = "not_unique", "Неуникальный"
    CAN_DISPUTE: str = 'can_dispute', "Закреплен, но можно оспорить"
    ERROR: str = 'error', "Ошибка"


class ResolveDisputeStatuses(StrEnum):
    UNIQUE: str = UserStatus.UNIQUE
    NOT_UNIQUE: str = UserStatus.NOT_UNIQUE


class SearchType(mixins.Choices):
    """
    Тип поиска
    """
    NAME: str = "name", "По имени"
    EMAIL: str = "email", "По почте"
    PHONE: str = "phone", "По телефону"


class CautionType(mixins.Choices):
    """
    Тип предупреждения
    """
    INFORMATION: str = "information", "Информация"
    WARNING: str = "warning", "Предупреждение"


class SlugType(mixins.Choices):
    """
    Тип Slug
    """
    MANAGER: str = "manager", "Менеджер"
    MINE: str = "mine", "Мой"


class UserPinningStatusType(mixins.Choices):
    """
    Статус закрепления пользователя
    """
    PINNED: str = "pinned", "Закреплен за вами"
    NOT_PINNED: str = "not_pinned", "Не закреплен"
    PARTIALLY_PINNED: str = "partially_pinned", "Закреплен за вами, но можно оспорить"
    UNKNOWN: str = "unknown", "Неизвестно"


class UserAssignSlug(StrEnum):
    """
    Тип Slug для страниц закрепления пользователя
    """
    CONFIRMED: str = "confirmed"
    UNASSIGNED: str = "unassigned"
    UNASSIGN: str = "unassign"


class OriginType(mixins.Choices):
    """
    Источник создания пользователя
    """
    AMOCRM: str = "amocrm", "Импорт из АМО CRM",
    SMS: str = "sms", "Авторизация через СМС"
    AGENT_ASSIGN: str = "agent_assign", "Закрепление агентом"


class UniqueStatusButtonSlug(StrEnum):
    """
    Слаг кнопки статуса уникальности
    """
    WANT_DISPUTE: str = "want_dispute"  # Хочу оспорить
    WANT_WORK: str = "want_work"  # Хочу работать с клиентом


DEFAULT_LIMIT = 20  # todo: refactor this
