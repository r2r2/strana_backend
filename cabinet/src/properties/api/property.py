# pylint: disable=no-member
from typing import Any

from http import HTTPStatus
from fastapi import APIRouter, Body, Request, Depends

from src.buildings import repos as buildings_repos
from src.floors import repos as floors_repos
from src.projects import repos as projects_repos
from src.properties import constants, models
from src.properties import repos as properties_repos
from src.properties import services, use_cases
from src.booking import repos as booking_repos
from src.amocrm import repos as amocrm_repos
from src.booking import tasks
from src.booking.services import ActivateBookingService, SendSmsToMskClientService
from src.notifications import repos as notifications_repos
from src.task_management import services as task_management_services
from src.task_management import repos as task_management_repos
from src.users import repos as users_repos
from src.properties.services import CheckProfitbasePropertyService

from common import utils, amocrm, requests, profitbase, dependencies, email, messages, security
from common.backend import repos as backend_repos
from config import session_config



router = APIRouter(prefix="/properties", tags=["Properties"])


@router.post("", status_code=HTTPStatus.CREATED, response_model=models.ResponseCreatePropertyModel)
async def create_property_view(
    request: Request, payload: models.RequestCreatePropertyModel = Body(...)
):
    """
    Создание объекта недвижимости
    """
    import_property_service: services.ImportPropertyService = services.ImportPropertyService(
        floor_repo=floors_repos.FloorRepo,
        global_id_decoder=utils.from_global_id,
        global_id_encoder=utils.to_global_id,
        project_repo=projects_repos.ProjectRepo,
        building_repo=buildings_repos.BuildingRepo,
        property_repo=properties_repos.PropertyRepo,
        building_booking_type_repo=buildings_repos.BuildingBookingTypeRepo,
        backend_building_booking_type_repo=backend_repos.BackendBuildingBookingTypesRepo,
        backend_properties_repo=backend_repos.BackendPropertiesRepo,
        backend_floors_repo=backend_repos.BackendFloorsRepo,
        backend_sections_repo=backend_repos.BackendSectionsRepo,
    )
    resources: dict[str, Any] = dict(
        session=request.session,
        session_config=session_config,
        property_repo=properties_repos.PropertyRepo,
        import_property_service=import_property_service,
    )
    create_property: use_cases.CreatePropertyCase = use_cases.CreatePropertyCase(**resources)
    return await create_property(payload=payload)


@router.get("/types", response_model=list[dict])
async def list_property_types():
    return [
        {"value": constants.PropertyTypes.FLAT, "label": constants.PropertyTypes.FLAT_LABEL},
        {"value": constants.PropertyTypes.PARKING, "label": constants.PropertyTypes.PARKING_LABEL},
        {
            "value": constants.PropertyTypes.COMMERCIAL,
            "label": constants.PropertyTypes.COMMERCIAL_LABEL,
        },
        {"value": constants.PropertyTypes.PANTRY, "label": constants.PropertyTypes.PANTRY_LABEL},
        {
            "value": constants.PropertyTypes.COMMERCIAL_APARTMENT,
            "label": constants.PropertyTypes.COMMERCIAL_APARTMENT_LABEL,
        },
    ]


@router.patch(
    "/bind",
    status_code=HTTPStatus.OK,
    response_model=models.ResponseBindBookingPropertyModel,
    dependencies=[Depends(dependencies.CurrentAnyTypeUserId())],
)
async def bind_booking_property(
    payload: models.RequestBindBookingPropertyModel = Body(...)
):
    """
    Связывание объекта недвижимости со сделкой
    """
    resources: dict[str, Any] = dict(
        booking_repo=booking_repos.BookingRepo,
        property_repo=properties_repos.PropertyRepo,
        building_booking_type_repo=buildings_repos.BuildingBookingTypeRepo,
        check_booking_task=tasks.check_booking_task,
        global_id_decoder=utils.from_global_id,
        request_class=requests.UpdateSqlRequest,
        amocrm_class=amocrm.AmoCRM,
        create_amocrm_log_task=tasks.create_amocrm_log_task,
        profitbase_class=profitbase.ProfitBase,
        create_booking_log_task=tasks.create_booking_log_task,
    )
    activate_bookings_service: ActivateBookingService = ActivateBookingService(**resources)
    resources: dict[str, Any] = dict(
        global_id_decoder=utils.from_global_id,
        profitbase_class=profitbase.ProfitBase,
    )
    check_profitbase_property_service = CheckProfitbasePropertyService(**resources)

    resources: dict[str, Any] = dict(
        task_instance_repo=task_management_repos.TaskInstanceRepo,
        task_status_repo=task_management_repos.TaskStatusRepo,
        booking_repo=booking_repos.BookingRepo,
    )
    update_status_service = task_management_services.UpdateTaskInstanceStatusService(
        **resources
    )

    resources: dict[str, Any] = dict(
        user_repo=users_repos.UserRepo,
        booking_repo=booking_repos.BookingRepo,
        template_repo=notifications_repos.AssignClientTemplateRepo,
        sms_class=messages.SmsService,
        hasher=security.get_hasher,
    )
    send_sms_to_msk_client: SendSmsToMskClientService = SendSmsToMskClientService(
        **resources
    )

    resources: dict[str, Any] = dict(
        property_repo=properties_repos.PropertyRepo,
        booking_repo=booking_repos.BookingRepo,
        building_booking_type_repo=buildings_repos.BuildingBookingTypeRepo,
        amocrm_status_repo=amocrm_repos.AmocrmStatusRepo,
        amocrm_class=amocrm.AmoCRM,
        activate_bookings_service=activate_bookings_service,
        change_booking_status_task=tasks.change_booking_status_task,
        update_task_instance_status_service=update_status_service,
        check_profitbase_property_service=check_profitbase_property_service,
        email_class=email.EmailService,
        sms_class=messages.SmsService,
        global_id_decoder=utils.from_global_id,
        send_sms_to_msk_client_service=send_sms_to_msk_client,
    )
    bind_property: use_cases.BindBookingPropertyCase = use_cases.BindBookingPropertyCase(**resources)
    return await bind_property(payload=payload)
