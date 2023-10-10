from http import HTTPStatus

from src.events_list.entities import BaseEventListException


class EventListNotFoundError(BaseEventListException):
    """
    Мероприятие не найдено.
    """
    message = "Мероприятие не найдено."
    status = HTTPStatus.NOT_FOUND
    reason = "event_list_not_found"
