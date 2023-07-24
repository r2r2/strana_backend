from http import HTTPStatus
from .entities import BaseRepresException


class RepresWrongPasswordError(BaseRepresException):
    message: str = "Введен неверный пароль."
    status: int = HTTPStatus.BAD_REQUEST
    reason: str = "repres_password_wrong"


class RepresNotApprovedError(BaseRepresException):
    message: str = "Представитель не одобрен."
    status: int = HTTPStatus.BAD_REQUEST
    reason: str = "repres_not_approved"


class RepresAlreadyRegisteredError(BaseRepresException):
    message: str = "Представитель уже зарегистрирован."
    status: int = HTTPStatus.BAD_REQUEST
    reason: str = "repres_already_registered"


class RepresNotFoundError(BaseRepresException):
    message: str = "Представитель не найден."
    status: int = HTTPStatus.BAD_REQUEST
    reason: str = "repres_not_found"


class RepresChangePasswordError(BaseRepresException):
    message: str = "Ошибка смены пароля."
    status: int = HTTPStatus.BAD_REQUEST
    reason: str = "repres_change_password"


class RepresConfirmEmailError(BaseRepresException):
    message: str = "Не подтверждена почта."
    status: int = HTTPStatus.BAD_REQUEST
    reason: str = "repres_email_confirm"


class RepresSamePasswordError(BaseRepresException):
    message: str = "Пароль остался неизменным."
    status: int = HTTPStatus.BAD_REQUEST
    reason: str = "repres_same_password"


class RepresPasswordTimeoutError(BaseRepresException):
    message: str = "Время смены истекло."
    status: int = HTTPStatus.BAD_REQUEST
    reason: str = "repres_password_timeout"


class RepresEmailTakenError(BaseRepresException):
    message: str = "Введенный email занят."
    status: int = HTTPStatus.BAD_REQUEST
    reason: str = "repres_email_taken"


class RepresNoAgencyError(BaseRepresException):
    message: str = "Агентство не найдено."
    status: int = HTTPStatus.BAD_REQUEST
    reason: str = "repres_no_agency"


class RepresPhoneTakenError(BaseRepresException):
    message: str = "Введенный телефон занят."
    status: int = HTTPStatus.BAD_REQUEST
    reason: str = "repres_phone_taken"


class RepresDataTakenError(BaseRepresException):
    message: str = "Введенные данные заняты."
    status: int = HTTPStatus.BAD_REQUEST
    reason: str = "repres_data_taken"


class RepresIncorrectPhoneFormatError(BaseRepresException):
    message: str = "Некорректный номер телефона"
    status: int = HTTPStatus.UNPROCESSABLE_ENTITY
    reason: str = "repres_incorrect_phone_format"
    
    
class RepresWasDeletedError(BaseRepresException):
    message: str = "Представитель был удален"
    status: int = HTTPStatus.BAD_REQUEST
    reason: str = "repres_was_deleted"


class RepresHasAgencyError(BaseRepresException):
    message: str = "У представителя уже есть агентство"
    status: int = HTTPStatus.BAD_REQUEST
    reason: str = "repres_has_agency_error"
