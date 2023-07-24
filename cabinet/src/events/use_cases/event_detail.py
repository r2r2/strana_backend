from typing import Type
from http import HTTPStatus

from src.agents.repos import AgentRepo, User

from fastapi import HTTPException
from src.users.constants import UserType
from ..entities import BaseEventCase
from ..exceptions import EventNotFoundError
from ..repos import (
    Event, EventParticipantRepo, EventParticipantStatus, EventRepo, EventType
)


class EventDetailCase(BaseEventCase):
    """
    Кейс для карточки мероприятия.
    """
    def __init__(
        self,
        event_repo: Type[EventRepo],
        event_participant_repo: Type[EventParticipantRepo],
        agent_repo: Type[AgentRepo],
    ) -> None:
        self.event_repo: EventRepo = event_repo()
        self.event_participant_repo: EventParticipantRepo = event_participant_repo()
        self.agent_repo: AgentRepo = agent_repo()

    async def __call__(
        self,
        event_id: int,
        user_id: int,
    ) -> Event:
        user: User = await self.agent_repo.retrieve(
            filters=dict(id=user_id),
            related_fields=["agency", "agency__city", "maintained", "maintained__city"],
        )

        if user.type not in [UserType.AGENT, UserType.REPRES]:
            raise HTTPException(
                status_code=HTTPStatus.FORBIDDEN,
                detail="Not authenticated",
                headers={"WWW-Authenticate": "Bearer"},
            )

        filters = dict(id=event_id, is_active=True)

        if user.type == UserType.AGENT:
            q_filters = [self.event_repo.q_builder(
                or_filters=[
                    dict(type=EventType.ONLINE),
                    dict(type=EventType.OFFLINE, show_in_all_cities=True),
                    dict(type=EventType.OFFLINE, city__name=user.agency.city.name),
                ]
            )]
        else:
            q_filters = [self.event_repo.q_builder(
                or_filters=[
                    dict(type=EventType.ONLINE),
                    dict(type=EventType.OFFLINE, show_in_all_cities=True),
                    dict(type=EventType.OFFLINE, city__name=user.maintained.city.name),
                ]
            )]

        agent_exist_in_participants_qs = self.event_participant_repo.list(
            filters=dict(
                event_id=self.event_repo.a_builder.build_outer("id"),
                agent_id=user.id,
                status=EventParticipantStatus.RECORDED,
            )
        )
        participants_count_qs = self.event_participant_repo.list(
            filters=dict(
                event_id=self.event_repo.a_builder.build_outer("id"),
                status=EventParticipantStatus.RECORDED,
            )
        )
        event: Event = await self.event_repo.retrieve(
            filters=filters,
            q_filters=q_filters,
            prefetch_fields=["city", "participants", "tags"],
            annotations=dict(
                agent_recorded=self.event_repo.a_builder.build_exists(agent_exist_in_participants_qs),
                participants_count=self.event_repo.a_builder.build_scount(participants_count_qs),
            ),
        )
        if not event:
            raise EventNotFoundError

        return event
