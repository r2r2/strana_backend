from datetime import datetime
from typing import Any

from src.events_list.entities import BaseEventListCase
from src.events_list.repos import EventListRepo, EventParticipantListRepo, EventParticipantList
from src.users.exceptions import UserNotFoundError
from src.users.repos import UserRepo, User


class EventListQRCodeCase(BaseEventListCase):
    def __init__(
        self,
        event_list_repo: type[EventListRepo],
        user_repo: type[UserRepo],
        event_participant_list_repo: type[EventParticipantListRepo],
    ):
        self.event_list_repo: EventListRepo = event_list_repo()
        self.user_repo: UserRepo = user_repo()
        self.event_participant_list_repo: EventParticipantListRepo = event_participant_list_repo()

    async def __call__(self, user_id: int) -> dict[str, Any] | None:
        user: User = await self.user_repo.retrieve(filters=dict(id=user_id))
        if not user:
            raise UserNotFoundError

        participant: EventParticipantList = await self.event_participant_list_repo.retrieve(
            filters=dict(phone=user.phone),
            related_fields=["event"],
        )
        if not participant:
            return

        if not all((participant.event.start_showing_date, participant.event.event_date)):
            return

        if participant.event.start_showing_date <= datetime.today().date() <= participant.event.event_date:
            # Текущая дата находится в промежутке между датой начала показа мероприятия и датой проведения мероприятия
            return dict(
                title=participant.event.title,
                subtitle=participant.event.subtitle,
                code=participant.code,
                event_date=participant.event.event_date,
                timeslot=participant.timeslot,
                text=participant.event.text,
            )
