from http import HTTPStatus
from typing import Any, Optional

from fastapi import APIRouter, Body, Depends, Header, Request

from common import (
    dependencies,
)
from src.booking import repos as booking_repos
from src.booking import use_cases, models
from src.users import constants as users_constants

router = APIRouter(prefix="/fast-booking", tags=["Fast Booking"])


@router.post(
    "/accept", status_code=HTTPStatus.CREATED, response_model=models.ResponseAcceptContractModel
)
async def fast_accept_contract_view(
    request: Request,
    payload: models.RequestFastAcceptContractModel = Body(...),
    origin: Optional[str] = Header(None),
    user_id: Optional[int] = Depends(
        dependencies.CurrentUserId(user_type=users_constants.UserType.CLIENT)
    ),
):
    """
    Принятие договора для быстрой брони
    """
    resources: dict[str, Any] = dict(
        booking_repo=booking_repos.BookingRepo,
    )
    fast_accept_contract: use_cases.FastAcceptContractCase = use_cases.FastAcceptContractCase(**resources)
    return await fast_accept_contract(payload=payload, user_id=user_id, origin=origin)
