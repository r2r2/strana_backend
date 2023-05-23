# pylint: skip-file
from http import HTTPStatus
from typing import Any, Literal, Optional, cast
from urllib.parse import parse_qs, unquote

import structlog

from common import (amocrm, dependencies, email, files, messages, profitbase,
                    requests, sberbank, security, utils)
from common.amocrm import repos as amocrm_repos
from common.backend import repos as backend_repos
from common.bazis import Bazis
from common.types import IAsyncFile
from config import (amocrm_config, backend_config, booking_config,
                    sberbank_config, session_config, site_config,
                    tortoise_config)
from fastapi import (APIRouter, BackgroundTasks, Body, Depends, File, Form,
                     Header, Path, Query, Request, UploadFile)
from fastapi.responses import RedirectResponse, StreamingResponse
from pydantic import Json, conint
from src.booking import filters, models
from src.booking import repos as booking_repos
from src.meetings import repos as meeting_repos
from src.booking import services as booking_services
from src.booking import tasks, use_cases
from src.booking import validations as booking_validators
from src.buildings import repos as buildings_repos
from src.floors import repos as floors_repos
from src.notifications import repos as notifications_repos
from src.projects import repos as projects_repos
from src.properties import repos as properties_repos
from src.properties import services as property_services
from src.properties.services import CheckProfitbasePropertyService
from src.task_management import repos as task_management_repos
from src.task_management import services as task_management_services
from src.task_management import use_cases as task_management_use_cases
from src.users import constants as users_constants
from src.users import repos as users_repos
from starlette.requests import ClientDisconnect
from tortoise import Tortoise

from ...agents.repos import AgentRepo
from ...users.services import CreateContactService
from ..maintenance import amocrm_webhook_maintenance
from ..tasks import create_booking_log_task

router = APIRouter(prefix="/booking", tags=["Booking"])


@router.post(
    "/accept", status_code=HTTPStatus.CREATED, response_model=models.ResponseBookingRetrieveModel
)
async def accept_contract_view(
    payload: models.RequestAcceptContractModel = Body(...),
    origin: Optional[str] = Header(None),
    user_id: Optional[int] = Depends(
        dependencies.CurrentUserId(user_type=users_constants.UserType.CLIENT)
    ),
):
    """
    Принятие договора
    """
    resources: dict[str, Any] = dict(
        global_id_decoder=utils.from_global_id,
        profitbase_class=profitbase.ProfitBase,
    )
    check_profitbase_property_service = CheckProfitbasePropertyService(**resources)
    resources: dict[str, Any] = dict(
        backend_config=backend_config,
        booking_config=booking_config,
        global_id_decoder=utils.from_global_id,
        booking_repo=booking_repos.BookingRepo,
        request_class=requests.UpdateSqlRequest,
        check_booking_task=tasks.check_booking_task,
        property_repo=properties_repos.PropertyRepo,
        create_booking_log_task=tasks.create_booking_log_task,
        check_profitbase_property_service=check_profitbase_property_service,
    )
    accept_contract: use_cases.AcceptContractCase = use_cases.AcceptContractCase(**resources)
    return await accept_contract(payload=payload, user_id=user_id, origin=origin)


@router.post(
    "/repeat", status_code=HTTPStatus.CREATED, response_model=models.ResponseBookingRetrieveModel
)
async def booking_repeat_view(
    payload: models.RequestBookingRepeatModel = Body(...),
    user_id: Optional[int] = Depends(
        dependencies.CurrentUserId(user_type=users_constants.UserType.CLIENT)
    ),
):
    """
    Повторное бронирование
    """
    resources: dict[str, Any] = dict(
        create_amocrm_log_task=tasks.create_amocrm_log_task,
        create_booking_log_task=tasks.create_booking_log_task,
        check_booking_task=tasks.check_booking_task,
        booking_repo=booking_repos.BookingRepo,
        amocrm_class=amocrm.AmoCRM,
        profitbase_class=profitbase.ProfitBase,
        global_id_decoder=utils.from_global_id,
        building_booking_type_repo=buildings_repos.BuildingBookingTypeRepo,
        property_repo=properties_repos.PropertyRepo,
        request_class=requests.UpdateSqlRequest,
    )
    activate_booking_class: booking_services.activate_booking = booking_services.ActivateBookingService(**resources)
    resources: dict[str, Any] = dict(
        global_id_decoder=utils.from_global_id,
        profitbase_class=profitbase.ProfitBase,
    )
    check_profitbase_property_service = CheckProfitbasePropertyService(**resources)
    resources: dict[str, Any] = dict(
        create_booking_log_task=tasks.create_booking_log_task,
        booking_repo=booking_repos.BookingRepo,
        global_id_decoder=utils.from_global_id,
        property_repo=properties_repos.PropertyRepo,
        request_class=requests.UpdateSqlRequest,
        backend_config=backend_config,
        booking_config=booking_config,
        check_booking_task=tasks.check_booking_task,
        check_profitbase_property_service=check_profitbase_property_service,
        activate_booking_class=activate_booking_class
    )
    booking_repeat: use_cases.BookingRepeat = use_cases.BookingRepeat(**resources)
    return await booking_repeat(booking_id=payload.booking_id, user_id=user_id)


@router.patch(
    "/fill/{booking_id}", status_code=HTTPStatus.OK, response_model=models.ResponseBookingRetrieveModel
)
async def fill_personal_view(
        booking_id: int = Path(...),
        payload: models.RequestFillPersonalModel = Body(...),
        user_id: Optional[int] = Depends(dependencies.CurrentUserId(user_type=users_constants.UserType.CLIENT)),
):
    """
    Заполнение персональных данных
    """
    resources: dict[str, Any] = dict(
        amocrm_class=amocrm.AmoCRM,
        global_id_decoder=utils.from_global_id,
        booking_repo=booking_repos.BookingRepo,
        profitbase_class=profitbase.ProfitBase,
        create_amocrm_log_task=tasks.create_amocrm_log_task,
        building_booking_type_repo=buildings_repos.BuildingBookingTypeRepo,
    )
    fill_personal: use_cases.FillPersonalCase = use_cases.FillPersonalCase(**resources)
    return await fill_personal(booking_id=booking_id, user_id=user_id, payload=payload)


@router.patch(
    "/check/{booking_id}", status_code=HTTPStatus.OK, response_model=models.ResponseBookingRetrieveModel
)
async def check_params_view(
    booking_id: int = Path(...),
    payload: models.RequestCheckParamsModel = Body(...),
    user_id: int = Depends(dependencies.CurrentUserId(user_type=users_constants.UserType.CLIENT)),
):
    """
    Проверка параметров
    """
    resources: dict[str, Any] = dict(
        sberbank_class=sberbank.Sberbank,
        global_id_decoder=utils.from_global_id,
        booking_repo=booking_repos.BookingRepo,
        create_booking_log_task=tasks.create_booking_log_task,
    )
    check_params: use_cases.CheckParamsCase = use_cases.CheckParamsCase(**resources)
    return await check_params(booking_id=booking_id, user_id=user_id, payload=payload)


@router.post(
    "/sberbank_link/{booking_id}",
    status_code=HTTPStatus.OK,
    response_model=models.ResponseSberbankLinkModel,
)
async def sberbank_link_view(
    booking_id: int = Path(...),
    payload: models.RequestSberbankLinkModel = Body(...),
    user_id: int = Depends(dependencies.CurrentUserId(user_type=users_constants.UserType.CLIENT)),
):
    """
    Получение ссылки сбербанка
    """
    resources: dict[str, Any] = dict(
        sberbank_class=sberbank.Sberbank,
        booking_repo=booking_repos.BookingRepo,
        global_id_decoder=utils.from_global_id,
        create_booking_log_task=tasks.create_booking_log_task,
    )
    sberbank_link: use_cases.SberbankLinkCase = use_cases.SberbankLinkCase(**resources)
    return await sberbank_link(booking_id=booking_id, user_id=user_id, payload=payload)


@router.get(
    "/sberbank/{secret}/{kind}",
    status_code=HTTPStatus.PERMANENT_REDIRECT,
    response_model=models.ResponseSberbankStatusModel,
)
async def sberbank_status_view(
    payment_id: str = Query(..., alias="orderId"),
    kind: Literal["success", "fail"] = Path(...),
    secret: str = Path(...),
):
    """
    Статус оплаты сбербанка
    """
    import_property_service: property_services.ImportPropertyService = property_services.ImportPropertyService(
        floor_repo=floors_repos.FloorRepo,
        global_id_decoder=utils.from_global_id,
        global_id_encoder=utils.to_global_id,
        project_repo=projects_repos.ProjectRepo,
        building_repo=buildings_repos.BuildingRepo,
        property_repo=properties_repos.PropertyRepo,
        building_booking_type_repo=buildings_repos.BuildingBookingTypeRepo,
        backend_building_booking_type_repo=backend_repos.BackendBuildingBookingTypesRepo,
        backend_floors_repo=backend_repos.BackendFloorsRepo,
        backend_sections_repo=backend_repos.BackendSectionsRepo,
        backend_properties_repo=backend_repos.BackendPropertiesRepo,
    )
    resources: dict[str, Any] = dict(
        orm_class=Tortoise,
        orm_config=tortoise_config,
        amocrm_class=amocrm.AmoCRM,
        backend_config=backend_config,
        user_repo=users_repos.UserRepo,
        agent_repo=AgentRepo,
        floor_repo=floors_repos.FloorRepo,
        user_types=users_constants.UserType,
        global_id_encoder=utils.to_global_id,
        request_class=requests.GraphQLRequest,
        booking_repo=booking_repos.BookingRepo,
        project_repo=projects_repos.ProjectRepo,
        building_repo=buildings_repos.BuildingRepo,
        property_repo=properties_repos.PropertyRepo,
        create_booking_log_task=create_booking_log_task,
        import_property_service=import_property_service,
        statuses_repo=amocrm_repos.AmoStatusesRepo,
        amocrm_config=amocrm_config,
    )
    import_bookings_service: booking_services.ImportBookingsService = booking_services.ImportBookingsService(
        **resources
    )
    history_service = booking_services.HistoryService(
        booking_history_repo=booking_repos.BookingHistoryRepo,
    )

    resources: dict[str, Any] = dict(
        task_instance_repo=task_management_repos.TaskInstanceRepo,
        task_status_repo=task_management_repos.TaskStatusRepo,
        booking_repo=booking_repos.BookingRepo,
    )
    update_task_instance_status_service = task_management_services.UpdateTaskInstanceStatusService(
        **resources
    )

    sberbank_status: use_cases.SberbankStatusCase = use_cases.SberbankStatusCase(
        site_config=site_config,
        amocrm_class=amocrm.AmoCRM,
        sms_class=messages.SmsService,
        booking_config=booking_config,
        email_class=email.EmailService,
        sberbank_config=sberbank_config,
        sberbank_class=sberbank.Sberbank,
        booking_repo=booking_repos.BookingRepo,
        global_id_decoder=utils.from_global_id,
        create_amocrm_log_task=tasks.create_amocrm_log_task,
        create_booking_log_task=tasks.create_booking_log_task,
        history_service=history_service,
        import_bookings_service=import_bookings_service,
        update_task_instance_status_service=update_task_instance_status_service,
    )
    return RedirectResponse(
        url=await sberbank_status(kind=kind, secret=secret, payment_id=payment_id)
    )


@router.post(
    "/amocrm/access_deal",
    status_code=HTTPStatus.OK,
    response_model=models.ResponseAmoCRMWebhookModel,
)
async def amocrm_webhook_access_deal_view(request: Request):
    """
    Вебхук АМО.

    Когда клиент отправляет данные для связи с банком или подаёт заявку на ипотеку на этапе выбора
    способа покупки, ему отображается экран "Подождите, введённые данные на проверке". Когда
    менеджер в AmoCRM подтвердит, вебхук придёт сюда.
    """
    try:
        payload: bytes = await request.body()
    except ClientDisconnect:
        return

    notification_service = booking_services.NotificationService(
        client_notification_repo=notifications_repos.ClientNotificationRepo
    )
    history_service = booking_services.HistoryService(
        booking_history_repo=booking_repos.BookingHistoryRepo,
    )
    amocrm_webhook_access_deal = use_cases.AmoCRMWebhookAccessDealCase(
        booking_repo=booking_repos.BookingRepo,
        create_booking_log_task=tasks.create_booking_log_task,
        webhook_request_repo=booking_repos.WebhookRequestRepo,
        email_class=email.EmailService,
        sms_class=messages.SmsService,
        history_service=history_service,
        notification_service=notification_service,
    )
    await amocrm_webhook_access_deal(payload=payload)


@router.post("/amocrm/date_deal", status_code=HTTPStatus.OK)
async def amocrm_webhook_date_deal_view(request: Request):
    """
    Вебхук АМО. Назначение дня подписания договора.
    """
    try:
        payload: bytes = await request.body()
    except ClientDisconnect:
        return

    notification_service = booking_services.NotificationService(
        client_notification_repo=notifications_repos.ClientNotificationRepo
    )
    history_service = booking_services.HistoryService(
        booking_history_repo=booking_repos.BookingHistoryRepo,
    )
    amocrm_webhook_date_deal = use_cases.AmoCRMWebhookDateDealCase(
        booking_repo=booking_repos.BookingRepo,
        create_booking_log_task=tasks.create_booking_log_task,
        webhook_request_repo=booking_repos.WebhookRequestRepo,
        email_class=email.EmailService,
        sms_class=messages.SmsService,
        history_service=history_service,
        notification_service=notification_service,
    )
    await amocrm_webhook_date_deal(payload=payload)


@router.post("/amocrm/deal_success", status_code=HTTPStatus.OK)
async def amocrm_webhook_deal_success_view(request: Request):
    """
    Вебхук АМО. Договор был подписан.
    """
    try:
        payload: bytes = await request.body()
    except ClientDisconnect:
        return

    notification_service = booking_services.NotificationService(
        client_notification_repo=notifications_repos.ClientNotificationRepo
    )
    history_service = booking_services.HistoryService(
        booking_history_repo=booking_repos.BookingHistoryRepo,
    )
    amocrm_webhook_deal_success = use_cases.AmoCRMWebhookDealSuccessCase(
        booking_repo=booking_repos.BookingRepo,
        create_booking_log_task=tasks.create_booking_log_task,
        webhook_request_repo=booking_repos.WebhookRequestRepo,
        email_class=email.EmailService,
        sms_class=messages.SmsService,
        history_service=history_service,
        notification_service=notification_service,
    )
    await amocrm_webhook_deal_success(payload=payload)


@router.post("/amocrm/documents_check", status_code=HTTPStatus.OK)
async def amocrm_webhook_change_status(request: Request) -> None:
    """
    Вебхук от АМО для обновления статуса задания
    """
    logger = structlog.get_logger("amocrm_webhook_change_status")
    try:
        payload: bytes = await request.body()
        logger.info(f"Received payload from AMO: {payload}")
    except ClientDisconnect:
        return
    data: dict[str, Any] = parse_qs(unquote(payload.decode("utf-8")))
    logger.info(f"Decoded payload from AMO: {data}")

    resources: dict[str, Any] = dict(
        task_instance_repo=task_management_repos.TaskInstanceRepo,
        task_status_repo=task_management_repos.TaskStatusRepo,
        booking_repo=booking_repos.BookingRepo,
    )
    update_task_instance_status_service = task_management_services.UpdateTaskInstanceStatusService(
        **resources
    )

    resources: dict[str, Any] = dict(
        booking_repo=booking_repos.BookingRepo,
        update_task_instance_status_service=update_task_instance_status_service,
    )
    update_task = task_management_use_cases.AmoCRMWebhookUpdateTaskInstanceCase(**resources)
    await update_task(data=data)


@router.post("/amocrm/notify_contact")
async def amocrm_webhook_notify_view(request: Request):
    """Вебхук для оповещения контакта"""
    try:
        import json
        payload = await request.body()
        print(f"{payload=}")
        # data: dict[str, Any] = parse_qs(unquote(payload.decode("utf-8")))
        data: dict[str, Any] = json.loads(payload)
        print(f"{data=}")
        amocrm_id_list = data.get("amocrm_id")
        print(f"{amocrm_id_list=}")
        if not amocrm_id_list:
            return
    except ClientDisconnect:
        return
    amocrm_id = int(amocrm_id_list[0])
    print(f"AMOCRM_ID: {amocrm_id}")
    resources = dict(
        amocrm_class=amocrm.AmoCRM,
        sms_class=messages.SmsService,
        booking_repo=booking_repos.BookingRepo,
        site_config=site_config,
        token_creator=security.create_access_token,
    )
    notify_case: use_cases.AmoCRMSmsWebhookCase = use_cases.AmoCRMSmsWebhookCase(**resources)

    return await notify_case(amocrm_id=amocrm_id)


@router.post("/amocrm/{secret}", status_code=HTTPStatus.OK)
@amocrm_webhook_maintenance
async def amocrm_webhook_view(request: Request, background_tasks: BackgroundTasks, secret: str = Path(...)):
    """
    Вебхук АМО
    """
    try:
        payload: bytes = await request.body()
    except ClientDisconnect:
        payload: bytes = bytes()
        secret: str = "wrong_secret"

    import_property_service: property_services.ImportPropertyService = property_services.ImportPropertyService(
        floor_repo=floors_repos.FloorRepo,
        global_id_decoder=utils.from_global_id,
        global_id_encoder=utils.to_global_id,
        project_repo=projects_repos.ProjectRepo,
        building_repo=buildings_repos.BuildingRepo,
        property_repo=properties_repos.PropertyRepo,
        building_booking_type_repo=buildings_repos.BuildingBookingTypeRepo,
        backend_building_booking_type_repo=backend_repos.BackendBuildingBookingTypesRepo,
        backend_floors_repo=backend_repos.BackendFloorsRepo,
        backend_sections_repo=backend_repos.BackendSectionsRepo,
        backend_properties_repo=backend_repos.BackendPropertiesRepo,
    )
    resources: dict[str, Any] = dict(
        orm_class=Tortoise,
        orm_config=tortoise_config,
        amocrm_class=amocrm.AmoCRM,
        backend_config=backend_config,
        user_repo=users_repos.UserRepo,
        agent_repo=AgentRepo,
        floor_repo=floors_repos.FloorRepo,
        user_types=users_constants.UserType,
        global_id_encoder=utils.to_global_id,
        request_class=requests.GraphQLRequest,
        booking_repo=booking_repos.BookingRepo,
        project_repo=projects_repos.ProjectRepo,
        building_repo=buildings_repos.BuildingRepo,
        property_repo=properties_repos.PropertyRepo,
        create_booking_log_task=create_booking_log_task,
        import_property_service=import_property_service,
        statuses_repo=amocrm_repos.AmoStatusesRepo,
        amocrm_config=amocrm_config,
    )
    import_bookings_service: booking_services.ImportBookingsService = booking_services.ImportBookingsService(
        **resources
    )
    resources: dict[str, Any] = dict(
        amocrm_class=amocrm.AmoCRM,
        user_repo=users_repos.UserRepo,
        import_bookings_service=import_bookings_service,
        amocrm_config=amocrm_config,
    )
    create_amocrm_contact_service: CreateContactService = CreateContactService(
        **resources
    )
    resources: dict[str, Any] = dict(
        backend_config=backend_config,
        booking_config=booking_config,
        check_booking_task=tasks.check_booking_task,
        sms_class=messages.SmsService,
        email_class=email.EmailService,
        user_repo=users_repos.UserRepo,
        booking_repo=booking_repos.BookingRepo,
        property_repo=properties_repos.PropertyRepo,
        building_booking_type_repo=buildings_repos.BuildingBookingTypeRepo(),
        amocrm_class=amocrm.AmoCRM,
        sql_request_class=requests.UpdateSqlRequest,
        token_creator=security.create_access_token,
        import_property_service=import_property_service,
        site_config=site_config,
        create_amocrm_contact_service=create_amocrm_contact_service,
        create_booking_log_task=create_booking_log_task,
        global_id_encoder=utils.to_global_id,
        global_id_decoder=utils.from_global_id,
    )
    fast_booking_webhook_case: use_cases.FastBookingWebhookCase = use_cases.FastBookingWebhookCase(**resources)

    resources: dict[str, Any] = dict(
        task_instance_repo=task_management_repos.TaskInstanceRepo,
        task_status_repo=task_management_repos.TaskStatusRepo,
        task_chain_repo=task_management_repos.TaskChainRepo,
        booking_repo=booking_repos.BookingRepo,
    )
    create_task_instance_service = task_management_services.CreateTaskInstanceService(
        **resources
    )

    resources: dict[str, Any] = dict(
        amocrm_class=amocrm.AmoCRM,
        amocrm_config=amocrm_config,
        backend_config=backend_config,
        request_class=requests.GraphQLRequest,
        booking_repo=booking_repos.BookingRepo,
        meeting_repo=meeting_repos.MeetingRepo,
        statuses_repo=amocrm_repos.AmoStatusesRepo,
        property_repo=properties_repos.PropertyRepo,
        create_booking_log_task=create_booking_log_task,
        webhook_request_repo=booking_repos.WebhookRequestRepo,
        fast_booking_webhook_case=fast_booking_webhook_case,
        background_tasks=background_tasks,
        create_task_instance_service=create_task_instance_service,
    )
    amocrm_webhook: use_cases.AmoCRMWebhookCase = use_cases.AmoCRMWebhookCase(**resources)
    return await amocrm_webhook(secret=secret, payload=payload)


@router.get("/single_email/{booking_id}", status_code=HTTPStatus.NO_CONTENT)
async def single_email_view(
    booking_id: int = Path(...),
    user_id: int = Depends(dependencies.CurrentUserId(user_type=users_constants.UserType.CLIENT)),
):
    """
    Отправка письма по одному бронированию
    """
    resources: dict[str, Any] = dict(
        email_class=email.EmailService,
        booking_repo=booking_repos.BookingRepo,
        create_booking_log_task=tasks.create_booking_log_task,
    )
    single_email: use_cases.SingleEmailCase = use_cases.SingleEmailCase(**resources)
    return await single_email(booking_id=booking_id, user_id=user_id)


@router.get("/mass_email", status_code=HTTPStatus.NO_CONTENT)
async def mass_email_view(
    user_id: int = Depends(dependencies.CurrentUserId(user_type=users_constants.UserType.CLIENT)),
):
    """
    Отправка писем по всем бронированиям
    """
    resources: dict[str, Any] = dict(
        email_class=email.EmailService,
        booking_repo=booking_repos.BookingRepo,
        create_booking_log_task=tasks.create_booking_log_task,
    )
    mass_email: use_cases.MassEmailCase = use_cases.MassEmailCase(**resources)
    return await mass_email(user_id=user_id)


@router.get("", status_code=HTTPStatus.OK, response_model=models.ResponseBookingListModel)
async def booking_list_view(
    user_id: int = Depends(dependencies.CurrentUserId(user_type=users_constants.UserType.CLIENT)),
    statuses: list[str] = Query([], description="Фильтры по статусам сделок", alias='status'),
    init_filters: models.BookingListFilters = Depends(),
):
    """
    Список бронирований
    """
    resources: dict[str, Any] = dict(booking_repo=booking_repos.BookingRepo)
    booking_list: use_cases.BookingListCase = use_cases.BookingListCase(**resources)
    return await booking_list(user_id=user_id, statuses=statuses, init_filters=init_filters)


@router.patch(
    "/admins/charge/{booking_id}",
    status_code=HTTPStatus.OK,
    response_model=models.ResponseAdminsBookingChargeModel,
    dependencies=[Depends(dependencies.CurrentUserId(user_type=users_constants.UserType.ADMIN))],
)
async def admins_booking_charge_view(
    booking_id: int = Path(...), payload: models.RequestAdminsBookingChargeModel = Body(...)
):
    """
    Изменение коммиссии администратором
    """
    resources: dict[str, Any] = dict(
        booking_repo=booking_repos.BookingRepo,
        notification_repo=notifications_repos.NotificationRepo,
    )
    admins_booking_charge: use_cases.AdminsBookingChargeCase = use_cases.AdminsBookingChargeCase(
        **resources
    )
    return await admins_booking_charge(booking_id=booking_id, payload=payload)


@router.get(
    "/history",
    status_code=HTTPStatus.OK,
    response_model=models.ResponseBookingHistoryModel,
)
async def history_view(
    user_id: int = Depends(dependencies.CurrentUserId(user_type=users_constants.UserType.CLIENT)),
    limit: conint(ge=0, le=40) = Query(20),
    offset: conint(ge=0) = Query(0),
):
    """
    История изменений данных по сделкам.
    """
    history_case = use_cases.HistoryCase(booking_history_repo=booking_repos.BookingHistoryRepo)
    return await history_case(user_id=user_id, limit=limit, offset=offset)


@router.get(
    "/{booking_id}", status_code=HTTPStatus.OK, response_model=models.ResponseBookingRetrieveModel
)
async def booking_retrieve_view(
    request: Request,
    booking_id: int = Path(...),
    user_id: int = Depends(dependencies.CurrentUserId(user_type=users_constants.UserType.CLIENT)),
):
    """
    Детальное бронирование
    """
    resources: dict[str, Any] = dict(
        session=request.session,
        session_config=session_config,
        booking_repo=booking_repos.BookingRepo,
    )
    booking_retrieve: use_cases.BookingRetrieveCase = use_cases.BookingRetrieveCase(**resources)
    return await booking_retrieve(booking_id=booking_id, user_id=user_id)


@router.delete("/{booking_id}", status_code=HTTPStatus.NO_CONTENT)
async def booking_delete_view(
    booking_id: int = Path(...),
    user_id: int = Depends(dependencies.CurrentUserId(user_type=users_constants.UserType.CLIENT)),
):
    """
    Удаление бронирования
    """
    resources: dict[str, Any] = dict(
        backend_config=backend_config,
        booking_repo=booking_repos.BookingRepo,
        amocrm_class=amocrm.AmoCRM,
        property_repo=properties_repos.PropertyRepo,
        profitbase_class=profitbase.ProfitBase,
        request_class=requests.UpdateSqlRequest,
        global_id_decoder=utils.from_global_id,
        create_booking_log_task=tasks.create_booking_log_task,
    )
    booking_delete: use_cases.BookingDeleteCase = use_cases.BookingDeleteCase(**resources)
    return await booking_delete(user_id=user_id, booking_id=booking_id)


@router.get(
    "/files/{booking_id}/{category}",
    status_code=HTTPStatus.OK,
)
async def stream_file_base64_view(
    booking_id: int = Path(...),
    user_id: int = Depends(dependencies.CurrentUserId(user_type=users_constants.UserType.CLIENT)),
    category: Literal["ddu_by_lawyer"] = Path(
        ..., description="Категория файла. Доступные значения: `ddu_by_lawyer`"
    ),
):
    """Стриминг файлов из S3 Bucket с кодировкой base64.

    Необходимо для pdf файла ДДУ, загруженным юристом. Были проблемы у фронта при использовании
    прямой ссылки на s3.
    """
    stream_file_base64_case = use_cases.StreamFileBase64Case(
        booking_repo=booking_repos.BookingRepo,
        file_client=files.FileClient,
    )
    encoded_file_generator = await stream_file_base64_case(
        booking_id=booking_id, user_id=user_id, category=category
    )
    return StreamingResponse(encoded_file_generator)


@router.post(
    "/purchase_start/{booking_id}",
    status_code=HTTPStatus.OK,
    response_model=models.ResponseBookingRetrieveModel,
)
async def purchase_start_view(
    booking_id: int = Path(...),
    user_id: int = Depends(dependencies.CurrentUserId(user_type=users_constants.UserType.CLIENT)),
):
    """
    Переход пользователя к онлайн-покупке
    """
    notification_service = booking_services.NotificationService(
        client_notification_repo=notifications_repos.ClientNotificationRepo
    )
    history_service = booking_services.HistoryService(
        booking_history_repo=booking_repos.BookingHistoryRepo,
    )
    purchase_start: use_cases.PurchaseStartCase = use_cases.PurchaseStartCase(
        backend_config=backend_config,
        booking_repo=booking_repos.BookingRepo,
        amocrm_class=amocrm.AmoCRM,
        create_booking_log_task=tasks.create_booking_log_task,
        history_service=history_service,
        notification_service=notification_service,
    )
    return await purchase_start(user_id=user_id, booking_id=booking_id)


@router.get(
    "/payment_method/combinations",
    status_code=HTTPStatus.OK,
    response_model=list[models.PaymentMethodCombination],
    dependencies=[Depends(dependencies.CurrentUserId(user_type=users_constants.UserType.CLIENT))]
)
async def payment_method_combinations_view():
    """
    payment method combinations
    """
    payment_method_combinations = use_cases.PaymentMethodCombinationsCase()
    return payment_method_combinations()


@router.post(
    "/payment_method/{booking_id}",
    status_code=HTTPStatus.OK,
    response_model=models.ResponseBookingRetrieveModel,
)
async def payment_method_select_view(
    booking_id: int = Path(...),
    user_id: int = Depends(dependencies.CurrentUserId(user_type=users_constants.UserType.CLIENT)),
    payload: models.RequestPaymentMethodSelectModel = Body(...),
):
    """
    Выбор способа покупки.

    Считаем, что в случае, когда `client_has_an_approved_mortgage` False,
    клиент хочет оформить заявку на ипотеку.
    """
    notification_service = booking_services.NotificationService(
        client_notification_repo=notifications_repos.ClientNotificationRepo
    )
    history_service = booking_services.HistoryService(
        booking_history_repo=booking_repos.BookingHistoryRepo,
    )
    payment_method_select = use_cases.PaymentMethodSelectCase(
        booking_repo=booking_repos.BookingRepo,
        bank_contact_info_repo=booking_repos.BankContactInfoRepo,
        amocrm_class=amocrm.AmoCRM,
        sms_class=messages.SmsService,
        email_class=email.EmailService,
        history_service=history_service,
        notification_service=notification_service,
    )
    return await payment_method_select(user_id=user_id, booking_id=booking_id, payload=payload)


@router.get(
    "/purchase_help_text/{booking_id}",
    status_code=HTTPStatus.OK,
    response_model=models.ResponseHelpTextModel,
)
async def purchase_help_text_view(
    booking_id: int = Path(...),
    user_id: int = Depends(dependencies.CurrentUserId(user_type=users_constants.UserType.CLIENT)),
):
    """Текст тултипа "Как купить онлайн?".

    Если в админке не будет найдено текста с типом покупки и стадией сделки,
    то выкинется тот, у которого default=True (или 404, если и такого нет).
    """
    case = use_cases.PurchaseHelpTextCase(
        booking_repo=booking_repos.BookingRepo,
        purchase_help_text_repo=booking_repos.PurchaseHelpTextRepo,
    )
    return await case(booking_id, user_id)


@router.post(
    "/ddu/{booking_id}/recognize_documents/",
    status_code=HTTPStatus.OK,
    response_model=models.ResponseRecognizeDocumentsModel,
)
async def recognize_documents_view(
    booking_id: int = Path(...),
    user_id: int = Depends(dependencies.CurrentUserId(user_type=users_constants.UserType.CLIENT)),
    passport_first_image: UploadFile = File(...),
):
    """Распознавание документов в БАЗИС-е."""
    case = use_cases.RecognizeDocumentsCase(
        booking_repo=booking_repos.BookingRepo,
        bazis_class=Bazis,
        file_validator=booking_validators.DDUUploadFileValidator,
    )
    return await case(
        booking_id=booking_id,
        user_id=user_id,
        passport_first_image=cast(IAsyncFile, passport_first_image),
    )


@router.post(
    "/ddu/{booking_id}/check_documents_recognized/{task_id}/",
    status_code=HTTPStatus.OK,
    response_model=models.ResponseCheckDocumentsRecognizedModel,
)
async def check_documents_recognized_view(
    booking_id: int = Path(...),
    task_id: str = Path(...),
    user_id: int = Depends(dependencies.CurrentUserId(user_type=users_constants.UserType.CLIENT)),
):
    """Проверка распознавания документов в БАЗИС-е."""
    case = use_cases.CheckDocumentsRecognizedCase(
        booking_repo=booking_repos.BookingRepo, bazis_class=Bazis
    )
    return await case(booking_id=booking_id, user_id=user_id, task_id=task_id)


@router.post(
    "/ddu/{booking_id}",
    status_code=HTTPStatus.CREATED,
    response_model=models.ResponseBookingRetrieveModel,
)
async def ddu_create_view(
    booking_id: int = Path(...),
    user_id: int = Depends(dependencies.CurrentUserId(user_type=users_constants.UserType.CLIENT)),
    payload: Json[models.RequestDDUCreateModel] = Form(...),
    registration_images: Optional[list[UploadFile]] = File(...),
    snils_images: Optional[list[UploadFile]] = File(...),
    birth_certificate_images: Optional[list[UploadFile]] = File(None),
    maternal_capital_certificate_image: Optional[UploadFile] = File(
        None, description="Сертификат из ПФР об остатке денежных средств на счете"
    ),
    maternal_capital_statement_image: Optional[UploadFile] = File(
        None, description="Справка из ПФР об остатке денежных средств на счете"
    ),
    housing_certificate_image: Optional[UploadFile] = File(
        None, description="Сертификат, который дают клиенту в организации, выдавшей сертификат"
    ),
    housing_certificate_memo_image: Optional[UploadFile] = File(
        None, description="Памятка, которую дают клиенту в организации, выдавшей сертификат"
    ),
):
    """
    Оформление ДДУ.

    В качестве **payload** нужно скидывать json dump. Такой подход вызван ограничениями **FastAPI**
    по работе с вложенными сущностями в **multipart/form-data**.

    *Пример тела запроса отобразится, если нажать **Try it out**, схему можно найти ниже
    страницы (`RequestDDUCreateModel`).*

    После создания ДДУ создаётся ссылка на форму загрузки ДДУ. Она не отдаётся в ответе endpoint-а,
    а должна отправляться в AmoCRM. Потом нужно уточнить способ работы.
    """
    notification_service = booking_services.NotificationService(
        client_notification_repo=notifications_repos.ClientNotificationRepo
    )
    history_service = booking_services.HistoryService(
        booking_history_repo=booking_repos.BookingHistoryRepo,
    )
    create_ddu = use_cases.DDUCreateCase(
        booking_repo=booking_repos.BookingRepo,
        ddu_repo=booking_repos.DDURepo,
        ddu_participant_repo=booking_repos.DDUParticipantRepo,
        file_processor=files.FileProcessor,
        amocrm_class=amocrm.AmoCRM,
        sms_class=messages.SmsService,
        email_class=email.EmailService,
        site_config=site_config,
        generate_online_purchase_id_class=booking_services.GenerateOnlinePurchaseIDService,
        ddu_data_from_participants_service=booking_services.DDUDataFromParticipantsService(),
        history_service=history_service,
        notification_service=notification_service,
        file_validator=booking_validators.DDUUploadFileValidator,
    )
    ddu_files: dict[str, Any] = dict(
        maternal_capital_certificate_image=maternal_capital_certificate_image,
        maternal_capital_statement_image=maternal_capital_statement_image,
        housing_certificate_image=housing_certificate_image,
        housing_certificate_memo_image=housing_certificate_memo_image,
    )
    participant_files: dict[str, list[Any]] = dict(
        registration_images=registration_images,
        snils_images=snils_images,
        birth_certificate_images=(
            [] if birth_certificate_images is None else birth_certificate_images
        ),
    )
    return await create_ddu(
        user_id=user_id,
        booking_id=booking_id,
        payload=cast(models.RequestDDUCreateModel, payload),
        ddu_files=ddu_files,
        participants_files=participant_files,
    )


@router.patch(
    "/ddu/{booking_id}",
    status_code=HTTPStatus.OK,
    response_model=models.ResponseBookingRetrieveModel,
)
async def ddu_update_view(
    booking_id: int = Path(...),
    user_id: int = Depends(dependencies.CurrentUserId(user_type=users_constants.UserType.CLIENT)),
    payload: Optional[Json[models.RequestDDUUpdateModel]] = Form(
        None, description="Строка. Json dump от `RequestDDUUpdateModel`"
    ),
    registration_images: Optional[list[UploadFile]] = File(None),
    inn_images: Optional[list[UploadFile]] = File(None),
    snils_images: Optional[list[UploadFile]] = File(None),
    birth_certificate_images: Optional[list[UploadFile]] = File(None),
):
    """
    Изменение ДДУ.

    В качестве **payload** нужно скидывать json dump. Такой подход вызван ограничениями **FastAPI**
    по работе с вложенными сущностями в **multipart/form-data**.

    *Пример тела запроса отобразится, если нажать **Try it out**, схему можно найти ниже
    страницы (`RequestDDUUpdateModel`).*

    Не обязательно указывать все поля в словарях участников.

    Изменение файлов участников:

    `participant_changes` представляет из себя массив словарей, в каждом из которых указан id
    участника. Если в этом словаре значение `*_image_changed` `True`, то будет выбран файл из массива
    файлов.

    К примеру, имеем 3 участника с id 1, 2, 3 и массив из двух файлов для изменения паспорта у 1-го
    и 3-го участника. Именно им и нужно указывать `registration_image_changed = True`, но не у 2-го.
    """
    history_service = booking_services.HistoryService(
        booking_history_repo=booking_repos.BookingHistoryRepo,
    )
    update_ddu = use_cases.DDUUpdateCase(
        booking_repo=booking_repos.BookingRepo,
        ddu_repo=booking_repos.DDURepo,
        ddu_participant_repo=booking_repos.DDUParticipantRepo,
        file_processor=files.FileProcessor,
        amocrm_class=amocrm.AmoCRM,
        ddu_data_from_participants_service=booking_services.DDUDataFromParticipantsService(),
        history_service=history_service,
    )
    participants_files: dict[str, list[Any]] = dict(
        registration_images=[] if registration_images is None else registration_images,
        inn_images=[] if inn_images is None else inn_images,
        snils_images=[] if snils_images is None else snils_images,
        birth_certificate_images=(
            [] if birth_certificate_images is None else birth_certificate_images
        ),
    )
    return await update_ddu(
        user_id=user_id,
        booking_id=booking_id,
        payload=cast(models.RequestDDUUpdateModel, payload),
        participants_files=participants_files,
    )


@router.get(
    "/ddu/upload/{booking_id}/{secret}",
    status_code=HTTPStatus.OK,
    response_model=models.ResponseDDUUploadRetrieveModel,
)
async def ddu_upload_retrieve_view(booking_id: int = Path(...), secret: str = Path(...)):
    """
    Загрузка ДДУ юристом.
    """
    ddu_upload = use_cases.DDUUploadRetrieveCase(booking_repo=booking_repos.BookingRepo)
    return await ddu_upload(booking_id=booking_id, secret=secret)


@router.post(
    "/ddu/upload/{booking_id}/{secret}",
    status_code=HTTPStatus.OK,
    response_model=models.ResponseDDUUploadRetrieveModel,
)
async def ddu_upload_view(
    booking_id: int = Path(...),
    secret: str = Path(...),
    ddu_file: Optional[UploadFile] = File(...),
):
    """
    Загрузка ДДУ юристом.
    """
    notification_service = booking_services.NotificationService(
        client_notification_repo=notifications_repos.ClientNotificationRepo
    )
    history_service = booking_services.HistoryService(
        booking_history_repo=booking_repos.BookingHistoryRepo,
    )
    ddu_upload = use_cases.DDUUploadCase(
        booking_repo=booking_repos.BookingRepo,
        file_processor=files.FileProcessor,
        sms_class=messages.SmsService,
        email_class=email.EmailService,
        history_service=history_service,
        notification_service=notification_service,
    )
    return await ddu_upload(booking_id=booking_id, secret=secret, ddu_file=ddu_file)


@router.post(
    "/ddu/accept/{booking_id}",
    status_code=HTTPStatus.OK,
    response_model=models.ResponseBookingRetrieveModel,
)
async def ddu_accept_view(
    booking_id: int = Path(...),
    user_id: int = Depends(dependencies.CurrentUserId(user_type=users_constants.UserType.CLIENT)),
):
    """
    Согласование договора. Пользователь нажал на кнопку "Ознакомился с договором".
    """
    notification_service = booking_services.NotificationService(
        client_notification_repo=notifications_repos.ClientNotificationRepo
    )
    history_service = booking_services.HistoryService(
        booking_history_repo=booking_repos.BookingHistoryRepo,
    )
    accept_ddu = use_cases.DDUAcceptCase(
        booking_repo=booking_repos.BookingRepo,
        ddu_repo=booking_repos.DDURepo,
        amocrm_class=amocrm.AmoCRM,
        sms_class=messages.SmsService,
        email_class=email.EmailService,
        history_service=history_service,
        notification_service=notification_service,
    )
    return await accept_ddu(user_id=user_id, booking_id=booking_id)


@router.post(
    "/ddu/escrow/{booking_id}",
    status_code=HTTPStatus.OK,
    response_model=models.ResponseBookingRetrieveModel,
)
async def escrow_upload_view(
    booking_id: int = Path(...),
    user_id: int = Depends(dependencies.CurrentUserId(user_type=users_constants.UserType.CLIENT)),
    escrow_file: Optional[UploadFile] = File(..., description="Документ об открытии эктроу-счёта"),
):
    """
    Договор на регистрации. Загрузка эскроу-счёта.

    Пока что можно несколько раз родряд отправлять запрос. Соответственно, доставать потом последний
    файл категории `escrow`. Мб стоит пересмотреть этот момент потом.
    """
    history_service = booking_services.HistoryService(
        booking_history_repo=booking_repos.BookingHistoryRepo
    )
    upload_escrow = use_cases.EscrowUploadCase(
        booking_repo=booking_repos.BookingRepo,
        ddu_repo=booking_repos.DDURepo,
        file_processor=files.FileProcessor,
        amocrm_class=amocrm.AmoCRM,
        history_service=history_service,
        file_validator=booking_validators.DDUUploadFileValidator,
    )
    return await upload_escrow(user_id=user_id, booking_id=booking_id, escrow_file=escrow_file)


@router.patch(
    "/superuser/fill/{booking_id}",
    status_code=HTTPStatus.OK,
)
def superuser_bookings_fill_data_view(
    booking_id: int = Path(...),
    data: str = Query(...),
):
    """
    Обновление сделок в АмоСРМ после изменения в админке брокера.
    """
    superuser_booking_fill_data_case: use_cases.SuperuserBookingFillDataCase = use_cases.SuperuserBookingFillDataCase(
        export_booking_in_amo_task=tasks.export_booking_in_amo,
    )
    return superuser_booking_fill_data_case(booking_id=booking_id, data=data)
