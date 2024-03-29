from http import HTTPStatus

from .entities import BaseNotificationException


class NotificationNotFoundError(BaseNotificationException):
    message: str = "Уведомление не найдено."
    status: int = HTTPStatus.NOT_FOUND
    reason: str = "notification_not_found"


class SMSTemplateNotFoundError(BaseNotificationException):
    message: str = "Шаблон смс не найден."
    status: int = HTTPStatus.NOT_FOUND
    reason: str = "sms_template_not_found"


class AssignClientTemplateNotFoundError(BaseNotificationException):
    message: str = "Шаблон смс для закрепления клиента не найден."
    status: int = HTTPStatus.NOT_FOUND
    reason: str = "assign_client_template_not_found"


class BookingNotificationNotFoundError(BaseNotificationException):
    message: str = "Уведомление для бронирования не найдено."
    status: int = HTTPStatus.NOT_FOUND
    reason: str = "booking_notification_not_found"


class PaymentPageNotificationNotFoundError(BaseNotificationException):
    message: str = "Шаблон оплаты не найден."
    status: int = HTTPStatus.NOT_FOUND
    reason: str = "payment_page_template_not_found"


class SendQRCodeSMSNotEnoughDataError(BaseNotificationException):
    message: str = "Не хватает данных для отправки смс с QR кодом."
    status: int = HTTPStatus.BAD_REQUEST
    reason: str = "send_qr_code_sms_not_enough_data"


class SMSTemplateNotActiveError(BaseNotificationException):
    message: str = "Шаблон смс не активен."
    status: int = HTTPStatus.BAD_REQUEST
    reason: str = "sms_template_not_active"
