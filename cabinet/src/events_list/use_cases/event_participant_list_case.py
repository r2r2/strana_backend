import asyncio
from typing import Awaitable, Any

from common.depreg import DepregAPI
from common.depreg.dto.depreg_response import DepregParticipantsDTO
from src.events_list.entities import BaseEventListCase
from src.events_list.exceptions import EventListNotFoundError
from src.events_list.repos import EventListRepo, EventParticipantListRepo, EventList, EventParticipantList


class EventParticipantListCase(BaseEventListCase):
    """
    Кейс обновления списка участников мероприятия по кнопке в админке.
    """

    def __init__(
        self,
        event_list_repo: type[EventListRepo],
        event_participant_list_repo: type[EventParticipantListRepo],
        depreg_api: type[DepregAPI],
    ):
        self.event_list_repo: EventListRepo = event_list_repo()
        self.event_participant_list_repo: EventParticipantListRepo = event_participant_list_repo()
        self.depreg_api: DepregAPI = depreg_api()

    async def __call__(self, event_id: int) -> None:
        event: EventList = await self.event_list_repo.retrieve(filters=dict(id=event_id))
        if not event:
            raise EventListNotFoundError

        participants: DepregParticipantsDTO = await self.get_participants(event_id=event_id)

        async_tasks: list[Awaitable] = []
        for participant in participants.data:
            data: dict[str, Any] = dict(
                phone=participant.phone,
                event=event,
                code=participant.code,
            )
            if p_list := await self._get_participant_list(event=event, phone=participant.phone):
                async_tasks.append(
                    self.event_participant_list_repo.update(model=p_list, data=data)
                )
            else:
                async_tasks.append(
                    self.event_participant_list_repo.create(data=data)
                )
        await asyncio.gather(*async_tasks)

    async def get_participants(self, event_id: int) -> DepregParticipantsDTO:
        async with self.depreg_api as depreg:
            response: DepregParticipantsDTO = await depreg.get_participants(event_id=event_id)
        return response

    async def _get_participant_list(self, event: EventList, phone: str) -> EventParticipantList | None:
        return await self.event_participant_list_repo.retrieve(filters=dict(event=event, phone=phone))
