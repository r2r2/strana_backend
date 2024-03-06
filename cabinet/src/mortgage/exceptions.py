from http import HTTPStatus

from src.mortgage.entities import BaseMortgageException


class MortgageFormNotFoundError(BaseMortgageException):
    """
    Форма ик не найдена.
    """
    message: str = "Форма ик не найдена"
    status: int = HTTPStatus.NOT_FOUND
    reason = "mortgage_form_not_found"


class NoAuthTokenError(BaseMortgageException):
    """
    Не передан токен авторизации.
    """
    message: str = "Не передан токен авторизации"
    status: int = HTTPStatus.UNAUTHORIZED
    reason = "no_auth_token"


class DocumentsNotFoundError(BaseMortgageException):
    """
    Документы не найдены.
    """
    message: str = "Загруженные документы не найдены"
    status: int = HTTPStatus.NOT_FOUND
    reason = "documents_not_found"
