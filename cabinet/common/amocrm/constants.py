from enum import StrEnum
from typing import Union


class AmoContactQueryWith(StrEnum):
    """
    Варианты значений для query поля with AmoCRM v4 contacts
    """
    leads = "leads"
    catalog_elements = "catalog_elements"
    customers = "customers"


class AmoCompanyEntityType(StrEnum):
    leads = "leads"
    contacts = "contacts"
    companies = "companies"
    customers = "customers"
    catalog_elements = "catalog_elements"


class AmoLeadQueryWith(StrEnum):
    """
    Варианты значений для query поля with AmoCRM v4 leads
    """
    catalog_elements = "catalog_elements"
    is_price_modified_by_robot = "is_price_modified_by_robot"
    loss_reason = "loss_reason"
    contacts = "contacts"
    only_deleted = "only_deleted"
    source_id = "source_id"


class AmoCompanyQueryWith(StrEnum):
    """
    Варианты значений для query поля with AmoCRM v4 companies
    """
    leads = "leads"
    catalog_elements = "catalog_elements"
    customers = "customers"
    contacts = "contacts"


class AmoEntityTypes:
    """Типы сущностей AmoCRM."""

    LEADS = "leads"
    CONTACTS = "contacts"
    AGENCIES = "companies"


class AmoTaskTypes:
    """Типы задач."""

    CALL = 1
    MEETING = 2
    WRITE_AN_EMAIL = 3


class AmoElementTypes:
    """Типы элементов для api/v2."""

    CONTACT = 1
    LEAD = 2
    COMPANY = 3
    CUSTOMER = 12


class AmoNoteTypes:
    """
    https://www.amocrm.ru/developers/content/crm_platform/events-and-notes#notes-types
    """
    COMMON = "common"  # Текстовое примечание


class BaseLeadSalesStatuses:
    START: Union[int, str, None] = None  # первичный контакт
    ASSIGN_AGENT: Union[int, str, None] = None  # Фиксация клиента за агентом
    MAKE_APPOINTMENT: Union[int, str, None] = None  # Назначить встречу
    MEETING: Union[int, str, None] = None  # Встреча назначена
    MEETING_IN_PROGRESS: Union[int, str, None] = None  # Идёт встреча
    MAKE_DECISION: Union[int, str, None] = None  # Принимают решение
    RE_MEETING: Union[int, str, None] = None  # Повторная встреча
    BOOKING: Union[int, str, None] = None  # бронь
    PAID_BOOKING: Union[int, str, None] = None  # платная бронь
    APPLY_FOR_A_MORTGAGE: Union[int, str, None] = None  # подать на ипотеку
    MORTGAGE_LEAD: Union[int, str, None] = None  # Заявка на ипотеку
    MORTGAGE_FILED: Union[int, str, None] = None  # ипотека подана
    MORTGAGE_DONE: Union[int, str, None] = None  # ипотека одобрена
    DDU_PROCESS: Union[int, str, None] = None  # оформление дду
    DDU_SIGNING: Union[int, str, None] = None  # подписание дду
    DDU_REGISTER: Union[int, str, None] = None  # мфц
    CONFIRMATION: Union[int, str, None] = None  # Подтверждение
    MONEY_PROCESS: Union[int, str, None] = None  # зачисление денег
    REALIZED: Union[int, str, None] = None  # успешно реализовано
    TERMINATION: Union[int, str, None] = None  # расторжение
    UNREALIZED: Union[int, str, None] = None  # Закрыто и не реализовано
