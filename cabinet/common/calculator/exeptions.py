from http import HTTPStatus


class BaseCalculatorException(Exception):
    message: str = "Ошибка интеграции с порталом"
    status: int = HTTPStatus.BAD_REQUEST
    reason: str = "portal_error"