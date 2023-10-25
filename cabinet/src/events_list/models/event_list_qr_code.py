from datetime import date

from src.events_list.entities import BaseEventListModel


class EventListQRCodeResponse(BaseEventListModel):
    """
    Модель ответа с QR-кодом.
    """

    code: str
    title: str | None
    subtitle: str | None
    event_date: date | None
    timeslot: str | None
    text: str
