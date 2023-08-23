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


class IncorrectBookingCreateMeetingError(BaseMeetingException):
    message: str = "Ошибка создания встречи из-за некорректной сделки."
    status: int = status.HTTP_400_BAD_REQUEST
    reason: str = "incorrect_booking_create_meeting_error"


class BookingStatusError(BaseMeetingException):
    message: str = "Сделка встречи находится в некорректном статусе"
    status: int = status.HTTP_400_BAD_REQUEST
    reason: str = "booking_status_error"


class MeetingAlreadyFinishError(BaseMeetingException):
    message: str = "Встреча уже завершена"
    status: int = status.HTTP_400_BAD_REQUEST
    reason: str = "meetings_already_finish_error"
