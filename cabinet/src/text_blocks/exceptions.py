from fastapi import status

from .entities import BaseTextBlockException


class TextBlockNotFoundError(BaseTextBlockException):
    message: str = "Текстовый блок не найден."
    status: int = status.HTTP_400_BAD_REQUEST
    reason: str = "meeting_not_found"


class AgentDataIncorrectError(BaseTextBlockException):
    message: str = "Переданные некорректные данные агента"
    status: int = status.HTTP_400_BAD_REQUEST
    reason: str = "agent_data_incorrect_error"
