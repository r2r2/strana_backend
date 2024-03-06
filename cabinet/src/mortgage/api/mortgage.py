from http import HTTPStatus
from typing import Any

from fastapi import APIRouter, Depends, Body, Path, Request, Query

from common import dependencies, amocrm
from common.calculator import CalculatorAPI
from src.amocrm.repos import AmocrmStatusRepo, AmocrmPipelineRepo
from src.booking import repos as booking_repos
from src.booking.repos import MortgageApplicationArchiveRepo
from src.cities.repos import CityRepo
from src.mortgage.models import (
    MortgageTextBlockResponseSchema,
    AmoStatusesPipelinesSchema,
    BookingsAgentsSchema,
    SendAmoDataSchema,
    ArchiveTicketStatusSchema,
    SendDDUFormSchema,
)
from src.mortgage.repos import (
    MortgageTextBlockRepo,
    PersonalInformationRepo,
)
from src.mortgage.use_cases import (
    GetMortgageTextBlockCase,
    GetAmoStatusesPipelinesCase,
    GetBookingsAgentsCase,
    SendAmoDataCase,
    ArchiveTicketStatusCase,
    SendDDUFormCase,
)
from src.questionnaire.repos import QuestionnaireUploadDocumentRepo
from src.task_management.factories import UpdateTaskInstanceStatusServiceFactory


router = APIRouter(prefix="/mortgage", tags=["Ипотека"])


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


@router.get(
    "/amocrm_statuses_pipelines",
    status_code=HTTPStatus.OK,
    response_model=AmoStatusesPipelinesSchema,
)
async def get_amocrm_statuses_pipelines():
    """
    Получение АМО статусов и воронок для сервиса ИК
    Эндпоинт вызывается по крону из сервиса ИК
    """
    resources: dict[str, Any] = dict(
        amocrm_status_repo=AmocrmStatusRepo,
        amocrm_pipeline_repo=AmocrmPipelineRepo,
    )

    get_amo_data: GetAmoStatusesPipelinesCase = GetAmoStatusesPipelinesCase(
        **resources
    )
    return await get_amo_data()


@router.get(
    "/bookings_agents_property",
    status_code=HTTPStatus.OK,
    response_model=list[BookingsAgentsSchema],
)
async def get_bookings_agents(
    user_id: int = Query(..., description="ID пользователя"),
):
    """
    Обновление бронирований и агентов в ИК,
    а так же инф по объекту недвижимости
    """
    resources: dict[str, Any] = dict(
        booking_repo=booking_repos.BookingRepo,
    )
    bookings_agents: GetBookingsAgentsCase = GetBookingsAgentsCase(
        **resources
    )
    return await bookings_agents(user_id=user_id)


@router.post(
    "/send_amo_data",
    status_code=HTTPStatus.OK,
    dependencies=[Depends(dependencies.CurrentAnyTypeUserId())],
)
async def send_amo_data(
    request: Request,
    payload: SendAmoDataSchema = Body(...),
):
    """
    Отправка запроса в мс Калькулятор, там отправка в АМО
    """
    resources: dict[str, Any] = dict(
        upload_document_repo=QuestionnaireUploadDocumentRepo,
        calculator_api=CalculatorAPI,
        personal_inf_repo=PersonalInformationRepo,
    )

    send_data: SendAmoDataCase = SendAmoDataCase(
        **resources
    )
    await send_data(payload=payload, request=request)


@router.post(
    "/archive_ticket_status",
    status_code=HTTPStatus.OK,
    dependencies=[Depends(dependencies.CurrentAnyTypeUserId())],
)
async def archive_ticket_status(
    request: Request,
    payload: ArchiveTicketStatusSchema = Body(...),
):
    """
    Вебхук из Калькулятора при изменении статуса заявки на ипотеку.
    Сохраняем в архив MortgageApplicationArchive
    """
    resources: dict[str, Any] = dict(
        archive_repo=MortgageApplicationArchiveRepo,
    )

    archive_data: ArchiveTicketStatusCase = ArchiveTicketStatusCase(
        **resources
    )
    await archive_data(payload=payload)


@router.post(
    "/ddu/send_form",
    status_code=HTTPStatus.OK,
    dependencies=[Depends(dependencies.CurrentAnyTypeUserId())],
)
async def send_ddu_form(
    payload: SendDDUFormSchema = Body(...),
):
    """
    Отправка формы ДДУ в АМО
    """
    update_task_instance_status_service = UpdateTaskInstanceStatusServiceFactory.create()
    resources: dict[str, Any] = dict(
        amocrm=amocrm.AmoCRM,
        booking_repo=booking_repos.BookingRepo,
        update_task_instance_status_service=update_task_instance_status_service,
    )
    send_form: SendDDUFormCase = SendDDUFormCase(**resources)
    await send_form(payload=payload)
