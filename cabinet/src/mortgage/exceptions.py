from http import HTTPStatus

from src.mortgage.entities import BaseMortgageException


class MortgageFormNotFoundError(BaseMortgageException):
    """
    Форма ик не найдена.
    """
    message: str = "Форма ик не найдена"
    status: int = HTTPStatus.NOT_FOUND
    reason = "mortgage_form_not_found"


class MortgageConditionMatrixNotFoundError(BaseMortgageException):
    """
    Матрица условий не найдена.
    """
    message: str = "Матрица условий не найдена"
    status: int = HTTPStatus.NOT_FOUND
    reason = "mortgage_condition_matrix_not_found"


class MortgageCalculatorConditionNotFoundError(BaseMortgageException):
    """
    Условие в калькуляторе не найдено.
    """
    message: str = "Условие в калькуляторе не найдено"
    status: int = HTTPStatus.NOT_FOUND
    reason = "mortgage_calculator_condition_not_found"


class MortgageProgramNotFoundError(BaseMortgageException):
    """
    Ипотечная программа не найдена.
    """
    message: str = "Ипотечная программа не найдена"
    status: int = HTTPStatus.NOT_FOUND
    reason = "mortgage_program_not_found"


class MortgageBankNotFoundError(BaseMortgageException):
    """
    Банк не найден.
    """
    message: str = "Банк не найден"
    status: int = HTTPStatus.NOT_FOUND
    reason = "mortgage_bank_not_found"


class MortgageApplicationStatusNotFoundError(BaseMortgageException):
    """
    Статус заявки не найден.
    """
    message: str = "Статус заявки не найден"
    status: int = HTTPStatus.NOT_FOUND
    reason = "mortgage_application_status_not_found"


class MortgageTicketNotFoundError(BaseMortgageException):
    """
    Заявка не найдена.
    """
    message: str = "Заявка на ипотеку не найдена"
    status: int = HTTPStatus.NOT_FOUND
    reason = "mortgage_ticket_not_found"
