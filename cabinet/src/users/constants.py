from enum import Enum

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


class UserStatusCheck(mixins.Choices):
    """
    Статус проверки пользователя
    """

    UNIQUE: str = "unique", "Уникальный"
    NOT_UNIQUE: str = "not_unique", "Неуникальный"
    CAN_DISPUTE: str = 'can_dispute', "Закреплен, но можно оспорить"
    ERROR: str = 'error', "Ошибка"


class ResolveDisputeStatuses(str, Enum):
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
