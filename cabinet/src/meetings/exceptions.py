from fastapi import status

from .entities import BaseMeetingException


class MeetingNotFoundError(BaseMeetingException):
    message: str = "Данная встреча не найдена."
    status: int = status.HTTP_404_NOT_FOUND
    reason: str = "meeting_not_found"


class MeetingsNotFoundError(BaseMeetingException):
    message: str = "Встречи не найдены."
    status: int = status.HTTP_404_NOT_FOUND
    reason: str = "meetings_not_found"


class IncorrectBookingCreateMeetingError(BaseMeetingException):
    message: str = "Ошибка создания встречи. Пожалуйста, проверьте корректность заполнения данных по сделке."
    status: int = status.HTTP_400_BAD_REQUEST
    reason: str = "incorrect_booking_create_meeting_error"


class BookingStatusError(BaseMeetingException):
    message: str = (
        'Ошибка создания встречи. Для создания сделка должна находиться в одном из следующих статусов: '
        '"Первичный контакт", "Назначить встречу", "Фиксация клиента за АН", "Встреча назначена", '
        '"Идет встреча", "Принимают решение", "Повторная встреча".'
                    )
    status: int = status.HTTP_400_BAD_REQUEST
    reason: str = "booking_status_error"


class MeetingAlreadyFinishError(BaseMeetingException):
    message: str = "Данная встреча уже завершена."
    status: int = status.HTTP_400_BAD_REQUEST
    reason: str = "meetings_already_finish_error"
