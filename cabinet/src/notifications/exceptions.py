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
