import asyncio
from typing import Coroutine

from src.events_list.entities import BaseEventListCase
from src.events_list.repos import (
    EventParticipantListRepo,
    EventParticipantList,
    EventGroupRepo,
    EventGroup,
)


class DeleteEventParticipantListCase(BaseEventListCase):
    def __init__(
        self,
        event_participant_list_repo: type[EventParticipantListRepo],
        event_group_repo: type[EventGroupRepo],
    ):
        self.event_participant_list_repo: EventParticipantListRepo = event_participant_list_repo()
        self.event_group_repo: EventGroupRepo = event_group_repo()

    async def __call__(self, event_id: int) -> None:
        participants_to_delete: list[EventParticipantList] = await self.event_participant_list_repo.list(
            filters=dict(event__event_id=event_id),
        )
        groups_to_delete: list[EventGroup] = await self.event_group_repo.list(
            filters=dict(event__event_id=event_id),
        )
        async_tasks: list[Coroutine | None] = [
            self._delete_collection(collection=participants_to_delete, repo=self.event_participant_list_repo),
            self._delete_collection(collection=groups_to_delete, repo=self.event_group_repo)
        ]
        await asyncio.gather(*async_tasks)

    async def _delete_collection(
        self,
        collection: list[EventParticipantList | EventGroup],
        repo: EventParticipantListRepo | EventGroupRepo,
    ) -> None:
        [asyncio.create_task(repo.delete(model=model)) for model in collection]
