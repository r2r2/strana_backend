from datetime import datetime
from typing import Any, Optional

from common import dependencies
from fastapi import APIRouter, Depends, Query, status
from src.agents import repos as agents_repos

from ..models import ResponseListCalendarEventModel
from ..repos import CalendarEventRepo, CalendarEventTypeSettingsRepo, EventParticipantRepo
from ..use_cases import CalendarEventListCase

router = APIRouter(prefix="/calendar", tags=["Calendar"])


@router.get(
    "",
    status_code=status.HTTP_200_OK,
    response_model=ResponseListCalendarEventModel,
)
async def calendar_event_list_view(
    calendar_event_type: Optional[str] = Query(
        default=None,
        description="Тип события календаря",
        alias='type',
    ),
    calendar_event_format_type: Optional[str] = Query(
        default=None,
        description="Тип формата события календаря",
        alias='formatType',
    ),
    date_start: Optional[datetime] = Query(
        default=None,
        description="Дата начала фильтрации событий календаря",
        alias="dateStart",
    ),
    date_end: Optional[datetime] = Query(
        default=None,
        description="Дата конца фильтрации событий календаря",
        alias="dateEnd",
    ),
    show_only_recorded_events: Optional[bool] = Query(
        default=None,
        description="Фильтр по записанным встречам",
        alias="showOnlyRecordedEvents",
    ),
    event_cities: list[str] = Query(
        [],
        description="Фильтр по городам встреч",
        alias="eventCity",
    ),
    meeting_statuses: list[str] = Query(
        [],
        description="Фильтр по статусам встреч событий календаря",
        alias='meetingStatus',
    ),
    meeting_client: Optional[str] = Query(
        default=None,
        description="Фильтр по клиенту встречи",
        alias='search',
    ),
    booking_id: Optional[int] = Query(
        default=None,
        description="Фильтр по сделке клиента",
        alias='bookingId',
    ),
    user_id: int = Depends(dependencies.CurrentAnyTypeUserId()),
):
    """
    Апи списка событий календаря.
    """
    resources: dict[str, Any] = dict(
        calendar_event_repo=CalendarEventRepo,
        event_participant_repo=EventParticipantRepo,
        calendar_event_type_settings_repo=CalendarEventTypeSettingsRepo,
        agent_repo=agents_repos.AgentRepo,
    )
    calendar_event_list_case: CalendarEventListCase = CalendarEventListCase(**resources)
    return await calendar_event_list_case(
        user_id=user_id,
        calendar_event_type=calendar_event_type,
        calendar_event_format_type=calendar_event_format_type,
        date_start=date_start,
        date_end=date_end,
        show_only_recorded_events=show_only_recorded_events,
        event_cities=event_cities,
        meeting_statuses=meeting_statuses,
        meeting_client=meeting_client,
        booking_id=booking_id,
    )
