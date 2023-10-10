from http import HTTPStatus


class DepregAPIError(Exception):
    message: str = "Ошибка интеграции с Департаментом Регистрации"
    status: int = HTTPStatus.BAD_REQUEST
    reason: str = "depreg_error"
