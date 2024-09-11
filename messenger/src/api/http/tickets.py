from datetime import date

from fastapi import APIRouter, Depends, HTTPException, Path, Query, status

from src.api.http.serializers.statistics import TicketsStatisticsResponse
from src.api.http.serializers.tickets import (
    CloseTicketRequest,
    CreateTicketRequest,
    CreateTicketResponse,
    TicketInfo,
    TicketStatusFilter,
    TicketUnreadCountersResponse,
    parse_tickets_filters,
)
from src.api.http.serializers.users import ResponseWithUserData
from src.constants import INT32_MAX
from src.controllers.statistics import StatisticsController
from src.controllers.tickets import TicketsController
from src.controllers.unread_counters import CountersController
from src.controllers.user_data import UserDataAdapter
from src.entities.tickets import TicketFilters
from src.entities.users import AuthPayload
from src.exceptions import NotPermittedError
from src.modules.auth.dependencies import auth_required, supervisor_required
from src.modules.storage.dependencies import inject_storage
from src.modules.storage.interface import StorageProtocol
from src.modules.storage.models import Ticket

tickets_router = APIRouter(prefix="/tickets")


async def ticket_required(
    ticket_id: int = Path(..., ge=1, le=INT32_MAX),
    storage: StorageProtocol = Depends(inject_storage),
) -> Ticket:
    ticket = await storage.tickets.get_ticket_by_id(ticket_id=ticket_id)
    if not ticket:
        raise HTTPException(
            detail="Ticket not found",
            status_code=status.HTTP_404_NOT_FOUND,
        )

    return ticket


@tickets_router.get(
    "",
    summary="Search tickets",
    response_model_exclude_none=True,
    response_model_exclude_unset=True,
)
async def search_tickets(
    filters: TicketFilters = Depends(parse_tickets_filters),
    user: AuthPayload = Depends(auth_required),
    status: TicketStatusFilter | None = Query(None),
    offset: int = Query(default=0, description="Pagination offset", ge=0),
    limit: int = Query(default=20, description="Pagination limit", le=50, ge=1),
    controller: TicketsController = Depends(),
    user_data_adapter: UserDataAdapter = Depends(),
) -> ResponseWithUserData[list[TicketInfo]]:
    tickets, _total_count = await controller.search_tickets(
        user=user,
        status=status,
        filters=filters,
        limit=limit,
        offset=offset,
    )
    return await user_data_adapter.enrich_response(response=tickets)


@tickets_router.get(
    "/counters",
)
async def get_ticket_counter(
    user: AuthPayload = Depends(supervisor_required),
    controller: CountersController = Depends(),
) -> TicketUnreadCountersResponse:
    return await controller.get_ticket_counters(user)


@tickets_router.get(
    "/statistics",
    summary="Get ticket statistics",
)
async def get_ticket_statistics(
    for_user_id: int | None = Query(default=None),
    date_from: date = Query(),
    date_to: date = Query(),
    user: AuthPayload = Depends(supervisor_required),
    controller: StatisticsController = Depends(),
) -> TicketsStatisticsResponse:
    try:
        return await controller.get_tickets_statistics(
            user=user,
            for_user_id=for_user_id,
            date_from=date_from,
            date_to=date_to,
        )
    except NotPermittedError as exc:
        raise HTTPException(
            detail=exc.message,
            status_code=status.HTTP_403_FORBIDDEN,
        ) from exc


@tickets_router.post(
    "",
    summary="Create ticket",
    responses={
        status.HTTP_404_NOT_FOUND: {"description": "Chat not found"},
        status.HTTP_409_CONFLICT: {"description": "A ticket already exists for this chat"},
        status.HTTP_403_FORBIDDEN: {"description": "Permissions error"},
    },
)
async def create_ticket(
    request: CreateTicketRequest,
    user: AuthPayload = Depends(auth_required),
    controller: TicketsController = Depends(),
) -> CreateTicketResponse:
    return await controller.create_ticket(
        user=user,
        match_id=request.match_id,
        created_from_chat_id=request.created_from_chat_id,
        message=request.message,
    )


@tickets_router.get(
    "/{ticket_id}",
    summary="Get ticket info",
    responses={
        status.HTTP_404_NOT_FOUND: {"description": "Ticket not found"},
        status.HTTP_403_FORBIDDEN: {"description": "Permissions error"},
    },
    response_model_exclude_none=True,
    response_model_exclude_unset=True,
)
async def get_ticket(
    ticket_id: int,
    user: AuthPayload = Depends(auth_required),
    controller: TicketsController = Depends(),
    user_data_adapter: UserDataAdapter = Depends(),
) -> ResponseWithUserData[TicketInfo]:
    ticket = await controller.get_ticket_details(user=user, ticket_id=ticket_id)
    if not ticket:
        raise HTTPException(
            detail="Ticket not found",
            status_code=status.HTTP_404_NOT_FOUND,
        )

    return await user_data_adapter.enrich_response(ticket)


@tickets_router.post(
    "/{ticket_id}/take",
    summary="Take the ticket into work",
    responses={
        status.HTTP_404_NOT_FOUND: {"description": "Ticket not found"},
        status.HTTP_403_FORBIDDEN: {"description": "Ticket is assigned to other user"},
    },
)
async def take_into_work(
    ticket: Ticket = Depends(ticket_required),
    user: AuthPayload = Depends(supervisor_required),
    controller: TicketsController = Depends(),
) -> None:
    await controller.take_into_work(ticket=ticket, user=user)


@tickets_router.post(
    "/{ticket_id}/close",
    summary="Close the ticket",
    responses={
        status.HTTP_404_NOT_FOUND: {"description": "Ticket not found"},
        status.HTTP_403_FORBIDDEN: {"description": "Ticket is assigned to other user"},
    },
)
async def close_ticket(
    request: CloseTicketRequest,
    ticket: Ticket = Depends(ticket_required),
    user: AuthPayload = Depends(supervisor_required),
    controller: TicketsController = Depends(),
) -> None:
    await controller.close_ticket(
        ticket=ticket,
        user=user,
        close_reason=request.close_reason,
        comment=request.comment,
    )


@tickets_router.post(
    "/{ticket_id}/confirm",
    summary="Confirm the completion of the ticket",
    description=(
        "Confirm the completion of the ticket. Available only for SOLVED tickets. Confirmed ticket cannot be reopened."
    ),
)
async def confirm_ticket(
    ticket: Ticket = Depends(ticket_required),
    user: AuthPayload = Depends(auth_required),
    controller: TicketsController = Depends(),
) -> None:
    await controller.confirm_ticket(ticket=ticket, user=user)


@tickets_router.post(
    "/{ticket_id}/reopen",
    summary="Reopen the ticket",
    description=(
        "Reopen the ticket and assign it to the user who closed it. Available only for closed tickets."
        "Available only for user who reported the ticket."
    ),
)
async def reopen_ticket(
    ticket: Ticket = Depends(ticket_required),
    user: AuthPayload = Depends(auth_required),
    controller: TicketsController = Depends(),
) -> None:
    await controller.reopen_ticket(ticket=ticket, user=user)
