from http import HTTPStatus

from src.cautions.entities import BaseCautionException


class CautionNotFoundError(BaseCautionException):
    message: str = "Предупреждение с таким ID не найдено"
    status: int = HTTPStatus.NOT_FOUND
    reason: str = "caution_not_found"
