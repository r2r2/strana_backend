from datetime import date

from fastapi import HTTPException, Query, status
from pydantic import BaseModel

from src.entities.matches import MatchFilters, MatchState, MatchStoredData
from src.providers.time import end_of_day, start_of_day


class MatchResponse(MatchStoredData):
    unread_count: int


class MatchListResponse(MatchStoredData):
    """Match short info response model"""


class StartChatWithScoutRequest(BaseModel):
    scout_user_id: int


class StartChatWithScoutResponse(BaseModel):
    chat_id: int


async def parse_match_filters(
    sport_ids: list[int] | None = Query(default=None, max_items=30, min_items=1, description="Filter by sports"),
    scout_numbers: list[int] | None = Query(
        default=None, max_items=30, min_items=1, description="Filter by scout numbers"
    ),
    match_date_from: date | None = Query(default=None, description="Filter by match date (from)"),
    match_date_to: date | None = Query(default=None, description="Filter by match date (to)"),
    search: str | None = Query(
        default=None,
        max_length=30,
        min_length=1,
        description="Search query",
    ),
    state: MatchState | None = Query(
        default=None,
        description="Filter by match state",
    ),
) -> MatchFilters:
    filter_date_from = start_of_day(match_date_from) if match_date_from else None
    filter_date_to = end_of_day(match_date_to) if match_date_to else None

    if match_date_from and match_date_to and match_date_from > match_date_to:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="match_date_from should be earlier than match_date_to",
        )

    return MatchFilters(
        match_date_from=filter_date_from,
        match_date_to=filter_date_to,
        scout_numbers=scout_numbers,
        sport_ids=sport_ids,
        search_query=search.strip() if search else None,
        state=state,
    )
