import datetime
from http import HTTPStatus
from typing import Any, Optional, Type

from fastapi import HTTPException
from pytz import UTC
from src.agents.repos import AgentRepo, User
from src.users.constants import UserType

from ..entities import BaseEventCase
from ..repos import (Event, EventParticipantRepo, EventParticipantStatus,
                     EventRepo, EventType)


class EventListCase(BaseEventCase):
    """
    Кейс для списка мероприятий.
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
        show_only_recorded_meetings: bool,
        user_id: int,
        date_start: Optional[datetime.datetime] = None,
        date_end: Optional[datetime.datetime] = None,
    ) -> dict[str, Any]:
        user: User = await self.agent_repo.retrieve(
            filters=dict(id=user_id),
            related_fields=["agency", "maintained"],
        )

        if user.type not in [UserType.AGENT, UserType.REPRES]:
            raise HTTPException(
                status_code=HTTPStatus.FORBIDDEN,
                detail="Not authenticated",
                headers={"WWW-Authenticate": "Bearer"},
            )

        filters = dict(is_active=True)
        if date_start and date_end:
            filters.update(dict(
                meeting_date_start__gte=date_start,
                meeting_date_start__lte=date_end,
            ))
        if show_only_recorded_meetings:
            filters.update(dict(
                participants__agent_id=user_id,
                participants__status=EventParticipantStatus.RECORDED,
            ))

        if user.type == UserType.AGENT:
            q_filters = [self.event_repo.q_builder(
                or_filters=[
                    dict(type=EventType.ONLINE),
                    dict(type=EventType.OFFLINE, show_in_all_cities=True),
                    dict(type=EventType.OFFLINE, city__name=user.agency.city),
                ]
            )]
        else:
            q_filters = [self.event_repo.q_builder(
                or_filters=[
                    dict(type=EventType.ONLINE),
                    dict(type=EventType.OFFLINE, show_in_all_cities=True),
                    dict(type=EventType.OFFLINE, city__name=user.maintained.city),
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
        events_query = self.event_repo.list(
            filters=filters,
            q_filters=q_filters,
            prefetch_fields=["city", "participants"],
            annotations=dict(
                agent_recorded=self.event_repo.a_builder.build_exists(agent_exist_in_participants_qs),
                participants_count=self.event_repo.a_builder.build_scount(participants_count_qs),
            ),
            ordering="-meeting_date_start",
        )
        events: list[Event] = await events_query
        count_events: int = await events_query.count()

        record_count: int = await self.event_repo.count(
            filters=dict(
                participants__agent_id=user_id,
                participants__status=EventParticipantStatus.RECORDED,
                meeting_date_start__gte=datetime.datetime.now(tz=UTC),
            )
        )

        return dict(
            count=count_events,
            record_count=record_count,
            result=events,
        )
