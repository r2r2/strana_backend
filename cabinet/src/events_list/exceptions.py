from http import HTTPStatus

from src.events_list.entities import BaseEventListException


class EventListNotFoundError(BaseEventListException):
    """
    Мероприятие не найдено.
    """
    message = "Мероприятие не найдено."
    status = HTTPStatus.NOT_FOUND
    reason = "event_list_not_found"


class EventParticipantListNotFoundError(BaseEventListException):
    """
    Список участников мероприятия не найден.
    """
    message = "Пользователь не найден в списке участников."
    status = HTTPStatus.NOT_FOUND
    reason = "event_participant_list_not_found"
