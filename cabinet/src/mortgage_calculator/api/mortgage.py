from http import HTTPStatus
from typing import Any

from fastapi import APIRouter, Depends, Body

from common import dependencies
from src.booking.models.booking_list import MortgageBookingListModel
from src.booking import repos as booking_repos
from src.mortgage_calculator.models import CreateMortgageTicketSchema
from src.mortgage_calculator.services import MortgageTicketCheckerService
from src.mortgage_calculator.use_cases import CreateMortgageTicketCase, GetMortgageBookingsCase


router = APIRouter(prefix="/mortgage", tags=["Ипотека"])


@router.post(
    "/create_ticket",
    status_code=HTTPStatus.NO_CONTENT,
    dependencies=[Depends(dependencies.CurrentAnyTypeUserId())],
)
async def create_mortgage_ticket(
    payload: CreateMortgageTicketSchema = Body(...),
):
    """
    Создание заявки на ипотеку
    """
    resources: dict[str, Any] = dict(

    )

    create_ticket: CreateMortgageTicketCase = CreateMortgageTicketCase(
        **resources
    )
    await create_ticket(payload=payload)


@router.get(
    "/bookings",
    status_code=HTTPStatus.OK,
    response_model=list[MortgageBookingListModel],
)
async def get_mortgage_bookings(
    user_id: int = Depends(dependencies.CurrentAnyTypeUserId()),
):
    """
    Получение списка бронирований для ипотеки
    """
    resources: dict[str, Any] = dict(
        booking_repo=booking_repos.BookingRepo,
        ticket_checker_service=MortgageTicketCheckerService,
    )

    get_bookings: GetMortgageBookingsCase = GetMortgageBookingsCase(
        **resources
    )
    return await get_bookings(user_id=user_id)
