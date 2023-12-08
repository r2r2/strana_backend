from http import HTTPStatus

from .entities import BaseSliderException

class SlideNotFoundError(BaseSliderException):
    """
    Ошибка отсутвия слайда
    """
    message: str = "Слайды не найдены."
    status: int = HTTPStatus.NOT_FOUND
    reason: str = "slides_not_found"
    