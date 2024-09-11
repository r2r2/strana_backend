from datetime import date, datetime
from enum import unique

from fastapi import HTTPException, Query, status
from pydantic import BaseModel, Field

from src.api.http.serializers.chats import ChatResponse
from src.constants import INT32_MAX
from src.core.common.utility import IntDocEnum
from src.entities.tickets import TicketCloseReason, TicketFilters, TicketStatus
from src.providers.time import end_of_day, start_of_day


@unique
class TicketStatusFilter(IntDocEnum):
    NEW = 1
    IN_PROGRESS = 2
    SOLVED = 3


class TicketMatchInfo(BaseModel):
    id: int | None
    team_a_name: str | None
    team_b_name: str | None
    sport_name: str | None
    sport_id: int | None
    start_at: datetime | None


class TicketInfo(BaseModel):
    chat_info: ChatResponse
    match_info: TicketMatchInfo

    ticket_id: int
    status: TicketStatus
    created_from_chat_id: int | None
    comment: str | None
    close_reason: TicketCloseReason | None
    ticket_created_at: datetime | None
    ticket_updated_at: datetime | None

    def get_referenced_user_ids(self) -> list[int]:
        return self.chat_info.get_referenced_user_ids()


class SearchTicketsResponse(BaseModel):
    count: int
    tickets: list[TicketInfo]


class CreateTicketRequest(BaseModel):
    match_id: int | None = None
    created_from_chat_id: int | None = None
    message: str = Field(..., max_length=2000)


class CreateTicketResponse(BaseModel):
    chat_id: int
    ticket_id: int


class CloseTicketRequest(BaseModel):
    comment: str = Field(..., max_length=2000)
    close_reason: TicketCloseReason


class TicketUnreadCountersResponse(BaseModel):
    by_ticket_status: dict[TicketStatus, int]


async def parse_tickets_filters(
    assigned_to_me: bool = Query(default=False, description="Show only tickets assigned to the current user"),
    match_id: int | None = Query(default=None, ge=1, le=INT32_MAX, description="Filter by match ID"),
    sport_ids: list[int] | None = Query(default=None, max_items=30, min_items=1, description="Filter by sports"),
    scout_numbers: list[int] | None = Query(
        default=None, max_items=30, min_items=1, description="Filter by scout numbers"
    ),
    match_date_from: date | None = Query(default=None, description="Filter by match date (from)"),
    match_date_to: date | None = Query(default=None, description="Filter by match date (to)"),
    ticket_date_from: date | None = Query(default=None, description="Filter by ticket date (from)"),
    ticket_date_to: date | None = Query(default=None, description="Filter by ticket date (to)"),
    search: str | None = Query(
        default=None,
        max_length=30,
        min_length=1,
        description="Search query",
    ),
) -> TicketFilters:
    if match_date_from and match_date_to and match_date_from > match_date_to:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="match_date_from should be earlier than match_date_to",
        )

    if ticket_date_from and ticket_date_to and ticket_date_from > ticket_date_to:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="ticket_date_from should be earlier than ticket_date_to",
        )

    filter_match_date_from = start_of_day(match_date_from) if match_date_from else None
    filter_match_date_to = end_of_day(match_date_to) if match_date_to else None
    filter_ticket_date_from = start_of_day(ticket_date_from) if ticket_date_from else None
    filter_ticket_date_to = end_of_day(ticket_date_to) if ticket_date_to else None

    return TicketFilters(
        match_date_from=filter_match_date_from,
        match_date_to=filter_match_date_to,
        sport_ids=sport_ids,
        scout_numbers=scout_numbers,
        ticket_date_from=filter_ticket_date_from,
        ticket_date_to=filter_ticket_date_to,
        match_id=match_id,
        assigned_to_me=assigned_to_me,
        search_query=search.strip() if search else None,
    )
