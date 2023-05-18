from fastapi import status

from .entities import BaseMeetingException


class MeetingNotFoundError(BaseMeetingException):
    message: str = "Встреча не найдена."
    status: int = status.HTTP_404_NOT_FOUND
    reason: str = "meeting_not_found"


class MeetingsNotFoundError(BaseMeetingException):
    message: str = "Встречи не найдены."
    status: int = status.HTTP_404_NOT_FOUND
    reason: str = "meetings_not_found"
