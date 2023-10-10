# pylint: disable=no-member
from typing import Any

from common import amocrm, dependencies, email, messages, profitbase, requests, security, utils
from config import amocrm_config, session_config, site_config
from fastapi import APIRouter, Body, Depends, Request, status
from src.booking import repos as booking_repos
from src.booking import tasks
from src.booking.factories import ActivateBookingServiceFactory
from src.booking.services import ActivateBookingService, SendSmsToMskClientService
from src.booking.services.deactivate_booking import DeactivateBookingService
from src.buildings import repos as buildings_repos
from src.properties import constants, models
from src.properties import repos as properties_repos
from src.properties import services, use_cases
from src.amocrm import repos as amocrm_repos
from src.properties.factories.services import CheckProfitbasePropertyServiceFactory
from src.task_management.factories import UpdateTaskInstanceStatusServiceFactory
from src.users import repos as users_repos
from src.users import services as user_services
from src.notifications import services as notification_services
from src.notifications import repos as notification_repos


router = APIRouter(prefix="/properties", tags=["Properties"])


@router.post("", status_code=status.HTTP_201_CREATED, response_model=models.ResponseCreatePropertyModel)
async def create_property_view(
    request: Request, payload: models.RequestCreatePropertyModel = Body(...)
):
    """
    Создание объекта недвижимости
    """
    import_property_service: services.ImportPropertyService = services.ImportPropertyServiceFactory.create()
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


@router.get(
    "/type_specs",
    status_code=status.HTTP_200_OK,
    response_model=list[models.ResponsePropertyTypeModel],
)
async def property_types_list_view():
    """
    Список типов объектов недвижимости из админки.
    """
    resources: dict[str, Any] = dict(
        property_type_repo=properties_repos.PropertyTypeRepo,
    )
    property_types_list: use_cases.PropertyTypeListCase = use_cases.PropertyTypeListCase(**resources)
    return await property_types_list()


@router.patch(
    "/bind",
    status_code=status.HTTP_200_OK,
    response_model=models.ResponseBindBookingPropertyModel,
    dependencies=[Depends(dependencies.CurrentAnyTypeUserId())],
)
async def bind_booking_property(
    payload: models.RequestBindBookingPropertyModel = Body(...)
):
    """
    Связывание объекта недвижимости со сделкой
    """
    activate_bookings_service: ActivateBookingService = ActivateBookingServiceFactory.create()
    check_profitbase_property_service = CheckProfitbasePropertyServiceFactory.create()
    update_status_service = UpdateTaskInstanceStatusServiceFactory.create()

    resources: dict[str, Any] = dict(
        user_repo=users_repos.UserRepo,
        booking_repo=booking_repos.BookingRepo,
        template_repo=notification_repos.AssignClientTemplateRepo,
        sms_class=messages.SmsService,
        hasher=security.get_hasher,
        site_config=site_config,
    )
    send_sms_to_msk_client: SendSmsToMskClientService = SendSmsToMskClientService(
        **resources
    )
    get_sms_template_service: notification_services.GetSmsTemplateService = \
        notification_services.GetSmsTemplateService(
            sms_template_repo=notification_repos.SmsTemplateRepo,
        )

    resources: dict[str, Any] = dict(
        amocrm_class=amocrm.AmoCRM,
        user_repo=users_repos.UserRepo,
        check_pinning_repo=users_repos.PinningStatusRepo,
        user_pinning_repo=users_repos.UserPinningStatusRepo,
        amocrm_config=amocrm_config,
    )
    check_pinning: user_services.CheckPinningStatusService = user_services.CheckPinningStatusService(**resources)

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
        get_sms_template_service=get_sms_template_service,
        send_sms_to_msk_client_service=send_sms_to_msk_client,
        check_pinning=check_pinning,
    )
    bind_property: use_cases.BindBookingPropertyCase = use_cases.BindBookingPropertyCase(**resources)
    return await bind_property(payload=payload)


@router.patch(
    "/unbind",
    status_code=status.HTTP_200_OK,
    dependencies=[Depends(dependencies.CurrentAnyTypeUserId())],
)
async def unbind_booking_property(
    payload: models.RequestUnbindBookingPropertyModel = Body(...),
):
    """
    Отвязывание объекта недвижимости от сделки
    """
    resources: dict[str, Any] = dict(
        booking_repo=booking_repos.BookingRepo,
        amocrm_class=amocrm.AmoCRM,
        profitbase_class=profitbase.ProfitBase,
        property_repo=properties_repos.PropertyRepo,
        request_class=requests.GraphQLRequest,
    )
    deactivate_booking_service: DeactivateBookingService = DeactivateBookingService(
        **resources
    )

    update_status_service = UpdateTaskInstanceStatusServiceFactory.create()

    resources: dict[str, Any] = dict(
        booking_repo=booking_repos.BookingRepo,
        deactivate_booking_service=deactivate_booking_service,
        update_status_service=update_status_service,
        amocrm_status_repo=amocrm_repos.AmocrmStatusRepo,
    )
    unbind_property: use_cases.UnbindBookingPropertyCase = use_cases.UnbindBookingPropertyCase(**resources)
    await unbind_property(payload=payload)
