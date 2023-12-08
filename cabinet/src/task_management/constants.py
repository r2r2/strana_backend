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


class ButtonCondition(mixins.Choices):
    """
    Условие кнопки
    """
    SUBMIT: str = "submit", "Отправить"


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


class MeetingsSlug(Slugs):
    """
    Слаги для Встреч
    """
    SIGN_UP: str = "meetings_sign_up"  # 1. Записаться на встречу
    AWAITING_CONFIRMATION: str = "meetings_awaiting_confirmation"  # 2. Ожидайте подтверждения встречи
    CONFIRMED_RESCHEDULED: str = "meetings_confirmed_rescheduled"  # 3. Встреча подтверждена, время перенесено
    CONFIRMED: str = "meetings_confirmed"  # 4. Встреча подтверждена

    CANCELED: str = "meetings_canceled"  # 6. Встреча отменена (Вы отменили встречу)
    CLIENT_CANCELED: str = "meetings_client_canceled"  # 7. Встреча отменена (Клиент отменил встречу)
    CLIENT_RESCHEDULED: str = "meetings_client_rescheduled"  # 8. Встреча отменена (Клиент перенес встречу)
    RESCHEDULED: str = "meetings_rescheduled"  # 9. Встреча перенесена (Вы перенесли встречу)
    START: str = "meetings_start"  # 10. Встреча началась
    FINISH: str = "meetings_finish"  # 11. Встреча завершена


class FixationExtensionSlug(Slugs):
    """
    Слаги для статусов задач фиксации клиентов брокерами.
    """
    NO_EXTENSION_NEEDED: str = "no_extension_needed"  # 1. Продление не требуется
    DEAL_NEED_EXTENSION: str = "deal_needs_extension"  # 2. Сделка нуждается в продлении
    CANT_EXTEND_DEAL_BY_ATTEMPT: str = "cant_extend_deal_by_attempt"  # 3. Нельзя продлить сделку из количества попыток
    DEAL_ALREADY_BOOKED: str = "deal_already_booked"  # 4. Сделка прошла статус бронирования
    CANT_EXTEND_DEAL_BY_DATE: str = "cant_extend_deal_by_date"  # 5. Нельзя продлить сделку из-за даты дедлайна


BOOKING_UPDATE_FIXATION_STATUSES = [
    "Первичный контакт",
    "Назначить встречу",
    "Фиксация клиента за АН",
    "Встреча назначена",
    "Идет встреча",
    "Принимают решение",
    "Повторная встреча",
]


class OnlineBookingSlug(Slugs):
    """
    Слаги для Онлайн бронирования
    """
    ACCEPT_OFFER: str = "online_booking_accept_offer"  # 1. Ознакомьтесь с договором офертой
    FILL_PERSONAL_DATA: str = "online_booking_fill_personal_data"  # 2. Заполните персональные данные
    CONFIRM_BOOKING: str = "online_booking_confirm_booking"  # 3. Подтвердите параметры бронирования
    PAYMENT: str = "online_booking_payment"  # 4. Оплатите бронирование
    PAYMENT_SUCCESS: str = "online_booking_payment_success"  # 5. Бронирование успешно оплачено
    TIME_IS_UP: str = "online_booking_time_is_up"  # 6. Время истекло
    CAN_EXTEND: str = "online_booking_can_extend"  # 7. Можно продлить бронирование
    CAN_NOT_EXTEND: str = "online_booking_can_not_extend"  # 8. Нельзя продлить бронирование


class FastBookingSlug(Slugs):
    """
    Слаги для Быстрого бронирования
    """
    ACCEPT_OFFER: str = "fast_booking_accept_offer"  # 1. Ознакомьтесь с договором офертой
    FILL_PERSONAL_DATA: str = "fast_booking_fill_personal_data"  # 2. Заполните персональные данные
    CONFIRM_BOOKING: str = "fast_booking_confirm_booking"  # 3. Подтвердите параметры бронирования
    PAYMENT: str = "fast_booking_payment"  # 4. Оплатите бронирование
    PAYMENT_SUCCESS: str = "fast_booking_payment_success"  # 5. Бронирование успешно оплачено
    TIME_IS_UP: str = "fast_booking_time_is_up"  # 6. Время истекло
    CAN_EXTEND: str = "fast_booking_can_extend"  # 7. Можно продлить бронирование
    CAN_NOT_EXTEND: str = "fast_booking_can_not_extend"  # 8. Нельзя продлить бронирование


class FreeBookingSlug(Slugs):
    """
    Слаги для Бесплатного бронирования
    """
    EXTEND: str = "free_booking_extend"  # 1. Продлить бесплатаную бронь
    ACCEPT_OFFER: str = "free_booking_accept_offer"  # 2. Ознакомьтесь с договором офертой
    FILL_PERSONAL_DATA: str = "free_booking_fill_personal_data"  # 3. Заполните персональные данные
    CONFIRM_BOOKING: str = "free_booking_confirm_booking"  # 4. Подтвердите параметры бронирования
    PAYMENT: str = "free_booking_payment"  # 5. Оплатите бронирование
    PAYMENT_SUCCESS: str = "free_booking_payment_success"  # 6. Бронирование успешно оплачено
    TIME_IS_UP: str = "free_booking_time_is_up"  # 7. Время истекло
    CAN_EXTEND: str = "free_booking_can_extend"  # 8. Можно продлить бронирование
    CAN_NOT_EXTEND: str = "free_booking_can_not_extend"  # 9. Нельзя продлить бронирование
