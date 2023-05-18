from http import HTTPStatus
from .entities import BaseAdminException


class AdminDataTakenError(BaseAdminException):
    message: str = "Введенные данные заняты."
    status: int = HTTPStatus.BAD_REQUEST
    reason: str = "admin_data_taken"


class AdminNotFoundError(BaseAdminException):
    message: str = "Администратор не найден."
    status: int = HTTPStatus.NOT_FOUND
    reason: str = "admin_not_found"


class AdminWrongPasswordError(BaseAdminException):
    message: str = "Введен неверный пароль."
    status: int = HTTPStatus.BAD_REQUEST
    reason: str = "admin_wrong_password"


class AdminWasDeletedError(BaseAdminException):
    message: str = "Администратор был удален"
    status: int = HTTPStatus.BAD_REQUEST
    reason: str = "admin_was_deleted"


class AdminConfirmEmailError(BaseAdminException):
    message: str = "Не подтверждена почта."
    status: int = HTTPStatus.BAD_REQUEST
    reason: str = "admin_email_confirm"


class AdminSamePasswordError(BaseAdminException):
    message: str = "Пароль остался неизменным."
    status: int = HTTPStatus.BAD_REQUEST
    reason: str = "admin_same_password"


class AdminPasswordTimeoutError(BaseAdminException):
    message: str = "Время смены истекло."
    status: int = HTTPStatus.BAD_REQUEST
    reason: str = "admin_password_timeout"


class AdminChangePasswordError(BaseAdminException):
    message: str = "Ошибка смены пароля."
    status: int = HTTPStatus.BAD_REQUEST
    reason: str = "admin_change_password"


class AdminIncorrectPhoneFormat(BaseAdminException):
    message: str = "Некорректный номер телефона"
    status: int = HTTPStatus.UNPROCESSABLE_ENTITY
    reason: str = "admin_incorrect_phone_format"
