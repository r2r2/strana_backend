from fastapi import status

from .entities import BaseEventException


class EventNotFoundError(BaseEventException):
    message: str = "Мероприятие не найдено"
    status: int = status.HTTP_400_BAD_REQUEST
    reason: str = "event_not_found"


class AgentAlreadySignupEventError(BaseEventException):
    message: str = "Агент уже записан на мероприятие"
    status: int = status.HTTP_400_BAD_REQUEST
    reason: str = "agent_already_signup_event"


class AgentHasNoSignupEventError(BaseEventException):
    message: str = "Агент не записан на мероприятие"
    status: int = status.HTTP_400_BAD_REQUEST
    reason: str = "agent_has_no_signup_event"


class EventHasNoPlacesError(BaseEventException):
    message: str = "На мероприятии нет свободных мест"
    status: int = status.HTTP_400_BAD_REQUEST
    reason: str = "event_has_no_places"


class EventHasAlreadyEndedError(BaseEventException):
    message: str = "Мероприятие уже закончилось"
    status: int = status.HTTP_400_BAD_REQUEST
    reason: str = "event_has_already_ended"
