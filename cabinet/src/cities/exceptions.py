from fastapi import status

from .entities import BaseCityException


class CityNotFoundError(BaseCityException):
    message: str = "Город не найден."
    status: int = status.HTTP_404_NOT_FOUND
    reason: str = "city_not_found"


class CitiesNotFoundError(BaseCityException):
    message: str = "Города не найдены."
    status: int = status.HTTP_404_NOT_FOUND
    reason: str = "cities_not_found"
