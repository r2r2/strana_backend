from fastapi import APIRouter, Depends

from src.api.http.serializers.compound import CompoundCountersResponse
from src.api.http.serializers.tickets import TicketUnreadCountersResponse
from src.controllers.unread_counters import CountersController
from src.entities.users import AuthPayload, Role
from src.modules.auth.dependencies import auth_required

compound_router = APIRouter(prefix="/compound")


@compound_router.get(
    "/counters",
    summary="Get unread counters for chats and tickets",
)
async def get_unread_counters(
    user: AuthPayload = Depends(auth_required),
    controller: CountersController = Depends(),
) -> CompoundCountersResponse:
    result = CompoundCountersResponse(
        chats=await controller.get_unread_counters(user),
        tickets=TicketUnreadCountersResponse(by_ticket_status={}),
    )

    if user.role == Role.SUPERVISOR:
        result.tickets = await controller.get_ticket_counters(user)

    return result
