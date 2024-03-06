from fastapi import status


class BaseTildaException(Exception):
    """
    Базовый класс для исключений Tilda
    """

    message: str
    status: int
    reason: str


class TildaIntegrationError(BaseTildaException):
    def __init__(
        self,
        message: str = "Ошибка интеграции с Tilda. Пожалуйста, повторите попытку позже.",
        reason: str = "tilda_exception",
    ):
        self.message = message
        self.reason = reason

    status: int = status.HTTP_502_BAD_GATEWAY
