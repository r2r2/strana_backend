from dataclasses import dataclass
from datetime import datetime
from enum import unique

from src.core.common.utility import IntDocEnum


@unique
class TicketStatus(IntDocEnum):
    NEW = 1
    IN_PROGRESS = 2
    SOLVED = 3
    CONFIRMED = 4


@unique
class TicketCloseReason(IntDocEnum):
    NO_SOLUTION_REQUIRED = 1
    TECHNICAL_PROBLEM_SOLVED = 2


@dataclass
class TicketFilters:
    assigned_to_me: bool | None = None
    match_id: int | None = None
    search_query: str | None = None
    sport_ids: list[int] | None = None
    scout_numbers: list[int] | None = None
    match_date_from: datetime | None = None
    match_date_to: datetime | None = None
    ticket_date_from: datetime | None = None
    ticket_date_to: datetime | None = None
