import datetime
import re
from http import HTTPStatus
from typing import Any, Optional, Type

from fastapi import HTTPException
from pytz import UTC
from src.agents.repos import AgentRepo, User
from src.users.constants import UserType

from ..entities import BaseEventCase
from ..repos import (CalendarEventRepo, CalendarEventTypeSettingsRepo, Event,
                     EventParticipantRepo, EventParticipantStatus, EventType)


class CalendarEventListCase(BaseEventCase):
    """
    Кейс для списка событий календаря.
    """
    def __init__(
        self,
        calendar_event_repo: Type[CalendarEventRepo],
        event_participant_repo: Type[EventParticipantRepo],
        calendar_event_type_settings_repo: Type[CalendarEventTypeSettingsRepo],
        agent_repo: Type[AgentRepo],

    ) -> None:
        self.calendar_event_repo: CalendarEventRepo = calendar_event_repo()
        self.event_participant_repo: EventParticipantRepo = event_participant_repo()
        self.calendar_event_type_settings_repo: CalendarEventTypeSettingsRepo = calendar_event_type_settings_repo()
        self.agent_repo: AgentRepo = agent_repo()

    async def __call__(
        self,
        user_id: int,
        event_cities: list[str],
        meeting_statuses: list[str],
        show_only_recorded_events: Optional[bool] = None,
        calendar_event_type: Optional[str] = None,
        calendar_event_format_type: Optional[str] = None,
        date_start: Optional[datetime.datetime] = None,
        date_end: Optional[datetime.datetime] = None,
        meeting_client: Optional[str] = None,
        booking_id: Optional[int] = None,
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

        # общие фильтры событий календаря
        filters = self.get_filter_data(
            event_cities=event_cities,
            meeting_statuses=meeting_statuses,
            calendar_event_type=calendar_event_type,
            calendar_event_format_type=calendar_event_format_type,
            date_start=date_start,
            date_end=date_end,
            booking_id=booking_id,
        )

        # общие q-фильтры событий календаря
        q_filters = self.get_q_filter_data(
            user=user,
            meeting_client=meeting_client,
        )

        calendar_event_type_settings_qs = self.calendar_event_type_settings_repo.retrieve(
            filters=dict(type=self.calendar_event_repo.a_builder.build_outer("type")),
        ).values("color")
        agent_exist_in_participants_qs: Any = self.event_participant_repo.exists(
            filters=dict(
                event_id=self.calendar_event_repo.a_builder.build_outer("event_id"),
                agent_id=user_id,
                status=EventParticipantStatus.RECORDED,
            ),
        )
        annotations: dict[str, Any] = dict(
            background_color=self.calendar_event_repo.a_builder.build_subquery(
                calendar_event_type_settings_qs
            ),
            has_record_on_event=self.calendar_event_repo.a_builder.build_exists(agent_exist_in_participants_qs),
        )

        calendar_events_query = self.calendar_event_repo.list(
            filters=filters,
            q_filters=q_filters,
            prefetch_fields=[
                "event",
                "event__city",
                "event__participants",
                "meeting",
                "meeting__status",
                "meeting__booking",
                "meeting__booking__user",
                "tags",
            ],
            ordering="-date_start",
            annotations=annotations,
        )
        calendar_events: list[Event] = await calendar_events_query

        if show_only_recorded_events:
            calendar_events = list(filter(lambda x: x.has_record_on_event is True, calendar_events))
            calendar_count_events = len(calendar_events)
        elif show_only_recorded_events is False:
            calendar_events = list(filter(lambda x: x.event_id and (x.has_record_on_event is False), calendar_events))
            calendar_count_events = len(calendar_events)
        else:
            calendar_count_events: int = await calendar_events_query.count()

        record_count: int = await self.calendar_event_repo.list(
            filters=dict(
                event__participants__agent_id=user_id,
                event__participants__status=EventParticipantStatus.RECORDED,
                event__meeting_date_start__gte=datetime.datetime.now(tz=UTC),
            ),
        ).count()

        return dict(
            count=calendar_count_events,
            record_count=record_count,
            result=calendar_events,
        )

    def get_filter_data(
        self,
        event_cities: list[str],
        meeting_statuses: list[str],
        calendar_event_type: Optional[str] = None,
        calendar_event_format_type: Optional[str] = None,
        date_start: Optional[datetime.datetime] = None,
        date_end: Optional[datetime.datetime] = None,
        booking_id: Optional[int] = None,
    ) -> dict:
        filters = dict()
        if booking_id:
            filters.update(dict(meeting__booking_id=booking_id))

        if calendar_event_type:
            filters.update(dict(type=calendar_event_type))

        if calendar_event_format_type:
            filters.update(dict(format_type=calendar_event_format_type))

        if date_start and date_end:
            filters.update(dict(
                date_start__gte=date_start,
                date_start__lte=date_end,
            ))

        if event_cities:
            filters.update(dict(event__city__slug__in=event_cities))

        if meeting_statuses:
            filters.update(dict(meeting__status__slug__in=meeting_statuses))

        return filters

    def get_q_filter_data(
        self,
        user: User,
        meeting_client: Optional[str] = None,
    ) -> list:
        if meeting_client:
            phone = re.sub(r'\D', '', meeting_client)
            meeting_client_q_filters = [self.calendar_event_repo.q_builder(
                or_filters=[
                    dict(
                        meeting__booking__user__email__icontains=meeting_client,
                        meeting__booking__agent_id=user.id,
                    ),
                    dict(
                        meeting__booking__user__phone__contains=phone,
                        meeting__booking__agent_id=user.id,
                    ) if phone else {},
                    dict(
                        meeting__booking__user__name__icontains=meeting_client,
                        meeting__booking__agent_id=user.id,
                    ),
                    dict(
                        meeting__booking__user__surname__icontains=meeting_client,
                        meeting__booking__agent_id=user.id,
                    ),
                    dict(
                        meeting__booking__user__patronymic__icontains=meeting_client,
                        meeting__booking__agent_id=user.id,
                    ),
                ]
            )]
            q_filters = meeting_client_q_filters
        else:
            if user.type == UserType.AGENT:
                event_city_q_filter = dict(
                    event__is_active=True,
                    event__type=EventType.OFFLINE,
                    event__city__name=user.agency.city,
                )
            else:
                event_city_q_filter = dict(
                    event__is_active=True,
                    event__type=EventType.OFFLINE,
                    event__city__name=user.maintained.city,
                )

            q_filters = [self.calendar_event_repo.q_builder(
                or_filters=[
                    event_city_q_filter,
                    dict(meeting__booking__agent_id=user.id),
                    dict(event__is_active=True, event__type=EventType.ONLINE),
                    dict(event__is_active=True, event__type=EventType.OFFLINE, event__show_in_all_cities=True),
                ]
            )]

        return q_filters
