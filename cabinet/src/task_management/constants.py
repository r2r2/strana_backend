from common import mixins
from src.task_management.helpers import Slugs


class TaskStatusType(mixins.Choices):
    """
    Тип статуса задачи
    """

    SUCCESS: str = "success", "Успех"
    ERROR: str = "error", "Ошибка"
    START: str = "start", "Начало"
    CHECK: str = "check", "Проверка"


class ButtonStyle(mixins.Choices):
    """
    Стиль кнопки
    """

    PRIMARY: str = "primary", "Основной"
    SECONDARY: str = "secondary", "Второстепенный"
    DANGER: str = "danger", "Опасный"
    WARNING: str = "warning", "Предупреждение"
    INFO: str = "info", "Информация"
    LIGHT: str = "light", "Светлый"
    DARK: str = "dark", "Темный"
    LINK: str = "link", "Ссылка"


class PaidBookingSlug(Slugs):
    """
    Слаги для Платного бронирования
    """

    START: str = "paid_booking_start"
    RE_BOOKING: str = "paid_booking_re_booking"
    WAIT_PAYMENT: str = "paid_booking_wait_for_payment"
    SUCCESS: str = "paid_booking_success"


class PackageOfDocumentsSlug(Slugs):
    """
    Слаги для Пакета документов
    """

    START: str = "Package_of_documents_Start"
    CHECK: str = "Package_of_documents_Check"
    SUCCESS: str = "Package_of_documents_Success"
    ERROR: str = "Package_of_documents_Error"
