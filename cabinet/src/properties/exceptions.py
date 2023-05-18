from http import HTTPStatus

from .entities import BasePropertyException


class PropertyTypeMissingError(BasePropertyException):
    message: str = "Тип не найден."
    status: int = HTTPStatus.BAD_REQUEST
    reason: str = "property_type_missing"


class PropertyNotFoundError(BasePropertyException):
    message: str = "Объект недвижимости не найден."
    status: int = HTTPStatus.BAD_REQUEST
    reason: str = "property_not_found"


class PropertyNotAvailableError(BasePropertyException):
    message: str = "Объект недвижимости недоступен."
    status: int = HTTPStatus.BAD_REQUEST
    reason: str = "property_not_available"
