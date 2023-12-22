from http import HTTPStatus
from typing import Any

from fastapi import APIRouter, Depends, Body, Path

from common import dependencies
from common.amocrm import amocrm
from src.booking import repos as booking_repos
from src.booking.models.booking_list import MortgageBookingListModel
from src.cities.repos import CityRepo
from src.mortgage.models import (
    CreateMortgageTicketSchema,
    MortgageTicketsResponseSchema,
    MortgageTextBlockResponseSchema,
)
from src.mortgage.repos import (
    MortgageDeveloperTicketRepo,
    MortgageFormRepo,
    MortgageBankRepo,
    MortgageProgramRepo,
    MortgageApplicationStatusRepo,
    MortgageConditionMatrixRepo,
    MortgageCalculatorConditionRepo,
    MortgageOfferRepo,
    MortgageTextBlockRepo,
)
from src.mortgage.services import MortgageTicketCheckerService
from src.mortgage.use_cases import (
    CreateMortgageTicketCase,
    GetMortgageBookingsCase,
    GetMortgageTicketListCase,
    GetMortgageTextBlockCase,
)


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
        mortgage_cond_matrix_repo=MortgageConditionMatrixRepo,
        mortgage_calc_cond_repo=MortgageCalculatorConditionRepo,
        mortgage_dev_ticket_repo=MortgageDeveloperTicketRepo,
        mortgage_form_repo=MortgageFormRepo,
        mortgage_bank_repo=MortgageBankRepo,
        mortgage_program_repo=MortgageProgramRepo,
        mortgage_application_status_repo=MortgageApplicationStatusRepo,
        mortgage_offer_repo=MortgageOfferRepo,
        booking_repo=booking_repos.BookingRepo,
        amocrm_class=amocrm.AmoCRM,
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


@router.get(
    "/tickets",
    status_code=HTTPStatus.OK,
    response_model=MortgageTicketsResponseSchema | None,
)
async def get_mortgage_tickets(
    user_id: int = Depends(dependencies.CurrentAnyTypeUserId()),
):
    """
    Получение списка заявок на ипотеку
    """
    resources: dict[str, Any] = dict(
        booking_repo=booking_repos.BookingRepo,
        mortgage_dev_ticket_repo=MortgageDeveloperTicketRepo,
        mortgage_status_repo=MortgageApplicationStatusRepo,
        mortgage_offer_repo=MortgageOfferRepo,
    )

    get_tickets: GetMortgageTicketListCase = GetMortgageTicketListCase(
        **resources
    )
    return await get_tickets(user_id=user_id)


@router.get(
    "/text_blocks/{city_slug}",
    status_code=HTTPStatus.OK,
    response_model=MortgageTextBlockResponseSchema | None,
    dependencies=[Depends(dependencies.CurrentAnyTypeUserId())],
)
async def get_mortgage_text_block(
    city_slug: str = Path(..., description="Слаг города")
):
    """
    Получение текстовых блоков для ипотеки
    """
    resources: dict[str, Any] = dict(
        mortgage_text_block_repo=MortgageTextBlockRepo,
        city_repo=CityRepo,
    )

    get_text_blocks: GetMortgageTextBlockCase = GetMortgageTextBlockCase(
        **resources
    )
    return await get_text_blocks(city_slug=city_slug)
