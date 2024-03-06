from fastapi import status

from .entities import BasePropertyException


class PropertyTypeMissingError(BasePropertyException):
    message: str = "Тип не найден."
    status: int = status.HTTP_400_BAD_REQUEST
    reason: str = "property_type_missing"


class PropertyNotFoundError(BasePropertyException):
    message: str = "Объект недвижимости не найден."
    status: int = status.HTTP_404_NOT_FOUND
    reason: str = "property_not_found"


class PropertiesNotFoundError(BasePropertyException):
    message: str = "Объекты недвижимости не найдены."
    status: int = status.HTTP_404_NOT_FOUND
    reason: str = "properties_not_found"


class PropertyNotAvailableError(BasePropertyException):
    message: str = "Объект недвижимости недоступен."
    status: int = status.HTTP_400_BAD_REQUEST
    reason: str = "property_not_available"


class PropertyImportError(BasePropertyException):
    message: str = "Ошибка импорта объекта недвижимости."
    status: int = status.HTTP_400_BAD_REQUEST
    reason: str = "property_import_error"


class PropertyIsNotFlatError(BasePropertyException):
    message: str = "Переданный объект не является квартирой"
    status: int = status.HTTP_400_BAD_REQUEST
    reason: str = "property_is_not_flat"
