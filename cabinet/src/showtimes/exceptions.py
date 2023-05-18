from http import HTTPStatus
from .entities import BaseShowTimeException


class ShowtimeNoClientError(BaseShowTimeException):
    message: str = "Клиент не зарегистрирован."
    status: int = HTTPStatus.BAD_REQUEST
    reason: str = "showtime_no_client"


class ShowtimeSlotTakenError(BaseShowTimeException):
    message: str = "Время записи занято."
    status: int = HTTPStatus.BAD_REQUEST
    reason: str = "showtime_slot_taken"


class ShowtimeNoProjectError(BaseShowTimeException):
    message: str = "Проект не найден."
    status: int = HTTPStatus.BAD_REQUEST
    reason: str = "project_not_found"


class ShowtimeIncorrectPhoneFormatError(BaseShowTimeException):
    message: str = "Некорректный номер телефона"
    status: int = HTTPStatus.UNPROCESSABLE_ENTITY
    reason: str = "showtime_incorrect_phone_format"
