from http import HTTPStatus
from typing import Any, Callable, Coroutine, Optional

from common import (amocrm, dependencies, email, messages, paginations,
                    requests, security, utils)
from common.amocrm import repos as amocrm_repos
from common.backend import repos as backend_repos
from config import (amocrm_config, backend_config, email_recipients_config,
                    session_config, site_config, tortoise_config)
from fastapi import (APIRouter, BackgroundTasks, Body, Depends, Header, Path,
                     Query, Request, Response)
from fastapi.responses import RedirectResponse
from src.admins import repos as admins_repos
from src.agencies import repos as agencies_repos
from src.agents import repos as agents_repos
from src.booking import repos as booking_repos
from src.booking import services as booking_services
from src.booking import tasks as bookings_tasks
from src.buildings import repos as buildings_repos
from src.cities import repos as cities_repos
from src.floors import repos as floors_repos
from src.projects import repos as projects_repos
from src.properties import repos as properties_repos
from src.properties import services as property_services
from src.task_management import repos as task_management_repos
from src.task_management import services as task_management_services
from src.users import constants as users_constants
from src.users import filters, models
from src.users import repos as users_repos
from src.users import services as user_services
from src.users import tasks as users_tasks
from src.users import use_cases
from src.represes import repos as represes_repos
from tortoise import Tortoise
from config import auth_config, session_config, site_config
from src.dashboard import repos as dashboard_repos
from src.dashboard import use_cases as dashboard_use_cases
from src.notifications import services as notification_services
from src.notifications import repos as notifications_repos


router = APIRouter(prefix="/users", tags=["Users"])
router_v2 = APIRouter(prefix="/v2/users", tags=["Users", "v2"])


@router.post("/send_code", status_code=HTTPStatus.OK, response_model=models.ResponseSendCodeModel)
async def send_code_view(
    background_tasks: BackgroundTasks,
    payload: models.RequestSendCodeModel = Body(...),
    x_real_ip: Optional[str] = Header(default=None),
):
    """
    Отправка кода
    """
    get_sms_template_service: notification_services.GetSmsTemplateService = \
        notification_services.GetSmsTemplateService(
            sms_template_repo=notifications_repos.SmsTemplateRepo,
        )
    send_code: use_cases.SendCodeCase = use_cases.SendCodeCase(
        hasher=security.get_hasher,
        sms_class=messages.SmsService,
        user_repo=users_repos.UserRepo,
        background_tasks=background_tasks,
        code_generator=utils.generate_code,
        password_generator=utils.generate_password,
        update_user_data=users_tasks.update_user_data_task,
        get_sms_template_service=get_sms_template_service,
    )
    return await send_code(payload=payload, real_ip=x_real_ip)


@router.post(
    "/validate_code", status_code=HTTPStatus.OK, response_model=models.ResponseValidateCodeModel,
)
async def validate_code_view(
    request: Request,
    payload: models.RequestValidateCodeModel = Body(...),
    x_real_ip: Optional[str] = Header(default=None),
):
    """
    Валидация кода
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
        backend_properties_repo=backend_repos.BackendPropertiesRepo,
        backend_floors_repo=backend_repos.BackendFloorsRepo,
        backend_sections_repo=backend_repos.BackendSectionsRepo,
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
        orm_class=Tortoise,
        orm_config=tortoise_config,
        amocrm_class=amocrm.AmoCRM,
        backend_config=backend_config,
        user_repo=users_repos.UserRepo,
        agent_repo=agents_repos.AgentRepo,
        floor_repo=floors_repos.FloorRepo,
        user_types=users_constants.UserType,
        global_id_encoder=utils.to_global_id,
        request_class=requests.GraphQLRequest,
        booking_repo=booking_repos.BookingRepo,
        project_repo=projects_repos.ProjectRepo,
        building_repo=buildings_repos.BuildingRepo,
        property_repo=properties_repos.PropertyRepo,
        create_booking_log_task=bookings_tasks.create_booking_log_task,
        import_property_service=import_property_service,
        statuses_repo=amocrm_repos.AmoStatusesRepo,
        amocrm_config=amocrm_config,
        check_pinning=check_pinning,
        check_booking_task=bookings_tasks.check_booking_task,
    )
    import_bookings_service: booking_services.ImportBookingsService = booking_services.ImportBookingsService(
        **resources,
    )
    resources: dict[str, Any] = dict(
        amocrm_class=amocrm.AmoCRM,
        user_repo=users_repos.UserRepo,
        import_bookings_service=import_bookings_service,
        amocrm_config=amocrm_config,
    )
    create_amocrm_contact_service: user_services.CreateContactService = user_services.CreateContactService(
        **resources,
    )
    resources: dict[str, Any] = dict(
        session=request.session,
        session_config=session_config,
        user_repo=users_repos.UserRepo,
        token_creator=security.create_access_token,
        create_amocrm_contact_service=create_amocrm_contact_service,
        amocrm_class=amocrm.AmoCRM,
        real_ip_repo=users_repos.RealIpUsersRepo,
        notification_mute_repo=users_repos.NotificationMuteRepo,
    )
    validate_code: use_cases.ValidateCodeCase = use_cases.ValidateCodeCase(**resources)
    return await validate_code(payload=payload, real_ip=x_real_ip)


@router.patch(
    "/update_personal", status_code=HTTPStatus.OK, response_model=models.ResponseUpdatePersonalModel
)
async def update_personal_view(
    payload: models.RequestUpdatePersonalModel = Body(...),
    user_id: int = Depends(dependencies.CurrentUserId(user_type=users_constants.UserType.CLIENT)),
):
    """
    Обновление персональных данных
    """
    get_email_template_service: notification_services.GetEmailTemplateService = \
        notification_services.GetEmailTemplateService(
            email_template_repo=notifications_repos.EmailTemplateRepo,
        )
    resources: dict[str, Any] = dict(
        site_config=site_config,
        amocrm_class=amocrm.AmoCRM,
        user_repo=users_repos.UserRepo,
        email_class=email.EmailService,
        token_creator=security.create_email_token,
        get_email_template_service=get_email_template_service,
    )
    update_personal: use_cases.UpdatePersonalCase = use_cases.UpdatePersonalCase(**resources)
    return await update_personal(payload=payload, user_id=user_id)


@router.get(
    "/session_token", status_code=HTTPStatus.OK, response_model=models.ResponseSessionTokenModel
)
async def session_token_view(request: Request):
    """
    Получение токена через сессию
    """
    resources: dict[str, Any] = dict(session=request.session, session_config=session_config)
    session_token: use_cases.SessionTokenCase = use_cases.SessionTokenCase(**resources)
    return await session_token()


@router.get("/me", status_code=HTTPStatus.OK, response_model=models.ResponseGetMeModel)
async def get_me_view(
    user_id: int = Depends(dependencies.CurrentUserId(user_type=users_constants.UserType.CLIENT)),
):
    """
    Получение текущего пользователя
    """
    resources: dict[str, Any] = dict(user_repo=users_repos.UserRepo)
    get_me: use_cases.GetMeCase = use_cases.GetMeCase(**resources)
    return await get_me(user_id=user_id)


@router.get(
    "/profile",
    status_code=HTTPStatus.OK,
    response_model=models.ResponseGetMeModel,
    summary="Профиль пользователя"
)
async def get_profile_view(
    user_id: int = Depends(dependencies.CurrentUserId(user_type=users_constants.UserType.CLIENT)),
):
    """
    API метод для получения профиля текущего пользователя
    """
    resources: dict[str, Any] = dict(user_repo=users_repos.UserRepo)
    get_profile: use_cases.GetMeCase = use_cases.GetMeCase(**resources)
    return await get_profile(user_id=user_id)


@router.post("/logout", status_code=HTTPStatus.NO_CONTENT)
async def process_logout_view(request: Request, response: Response):
    """
    Выход с удалением токена из сессии
    """
    resources: dict[str, Any] = dict(
        session=request.session,
        session_config=session_config,
        response=response,
        request=request,
    )
    process_logout: use_cases.ProcessLogoutCase = use_cases.ProcessLogoutCase(**resources)
    await process_logout()


@router.post("/update_last_activity", status_code=HTTPStatus.NO_CONTENT)
async def update_last_activity_view(request: Request):
    """
    Обновление времени последней активности
    """
    resources: dict[str, Any] = dict(session=request.session, session_config=session_config)
    update_last_activity: use_cases.UpdateLastActivityCase = use_cases.UpdateLastActivityCase(**resources)
    await update_last_activity()


@router.patch(
    "/change_phone", status_code=HTTPStatus.OK, response_model=models.ResponseChangePhoneModel
)
async def change_phone_view(
    user_id: int = Depends(dependencies.CurrentUserId(user_type=users_constants.UserType.CLIENT)),
    payload: models.RequestChangePhoneModel = Body(...),
):
    """
    Смена номера телефона
    """
    resources: dict[str, Any] = dict(user_repo=users_repos.UserRepo, amocrm_class=amocrm.AmoCRM)
    change_phone: use_cases.ChangePhoneCase = use_cases.ChangePhoneCase(**resources)
    return await change_phone(user_id=user_id, payload=payload)


@router.get("/confirm_email", status_code=HTTPStatus.PERMANENT_REDIRECT)
async def confirm_email_view(
    token: str = Query(..., alias="q"), email_token: str = Query(..., alias="p")
):
    """
    Подтверждение почты
    """
    resources: dict[str, Any] = dict(
        site_config=site_config,
        user_repo=users_repos.UserRepo,
        user_type=users_constants.UserType.CLIENT,
        token_decoder=security.decode_email_token,
    )
    confirm_email: use_cases.ConfirmEmailCase = use_cases.ConfirmEmailCase(**resources)
    return RedirectResponse(url=await confirm_email(token=token, email_token=email_token))


@router.patch(
    "/partial_update", status_code=HTTPStatus.OK, response_model=models.ResponsePartialUpdateModel
)
async def partial_update_view(
    payload: models.RequestPartialUpdateModel = Body(...),
    user_id: int = Depends(dependencies.CurrentUserId(user_type=users_constants.UserType.CLIENT)),
):
    """
    Частичное обновление
    """
    get_email_template_service: notification_services.GetEmailTemplateService = \
        notification_services.GetEmailTemplateService(
            email_template_repo=notifications_repos.EmailTemplateRepo,
        )
    resources: dict[str, Any] = dict(
        site_config=site_config,
        amocrm_class=amocrm.AmoCRM,
        user_repo=users_repos.UserRepo,
        email_class=email.EmailService,
        token_creator=security.create_email_token,
        get_email_template_service=get_email_template_service,
    )
    partial_update: use_cases.PartialUpdateCase = use_cases.PartialUpdateCase(**resources)
    return await partial_update(user_id=user_id, payload=payload)


@router.get(
    "/clients/interests",
    status_code=HTTPStatus.OK,
    response_model=models.ResponseInterestsList,
    dependencies=[Depends(dependencies.DeletedUserCheck())]
)
async def client_interests_view(
    user_id: int = Depends(dependencies.CurrentUserId(user_type=users_constants.UserType.CLIENT)),
    pagination: paginations.PagePagination = Depends(dependencies.Pagination()),
    init_filters: models.SlugTypeChoiceFilters = Depends()
):
    """
    Получение предпочтений пользователя
    """
    resources: dict[str: Any] = dict(
        user_interests_repo=users_repos.InterestsRepo,
    )
    user_case: use_cases.UsersInterestsListCase = use_cases.UsersInterestsListCase(**resources)
    return await user_case(user_id=user_id, pagination=pagination, init_filters=init_filters)


@router.patch(
    "/clients/interests",
    status_code=HTTPStatus.OK,
    response_model=models.ResponseUsersInterestModel,
    dependencies=[Depends(dependencies.DeletedUserCheck())],
)
async def client_interest_view(
    interested_global_ids: list[str] = Body(...),
    user_id: int = Depends(dependencies.CurrentUserId(user_type=users_constants.UserType.CLIENT)),
):
    """
    Добавление предпочтений пользователем
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
        backend_properties_repo=backend_repos.BackendPropertiesRepo,
        backend_floors_repo=backend_repos.BackendFloorsRepo,
        backend_sections_repo=backend_repos.BackendSectionsRepo,
        backend_special_offers_repo=backend_repos.BackendSpecialOfferRepo,
    )
    resources: dict[str, Any] = dict(
        user_repo=users_repos.UserRepo,
        property_repo=properties_repos.PropertyRepo,
        interests_repo=users_repos.InterestsRepo,
        agency_repo=agencies_repos.AgencyRepo,
        import_property_service=import_property_service,
    )
    users_interest_case: use_cases.UsersInterestGlobalIdCase = use_cases.UsersInterestGlobalIdCase(
        **resources
    )
    return await users_interest_case(user_id=user_id, interested_global_ids=interested_global_ids)


@router.patch(
    "/clients/uninterests",
    status_code=HTTPStatus.OK,
    response_model=models.ResponseUsersUninterestModel,
    dependencies=[Depends(dependencies.DeletedUserCheck())],
)
async def clients_users_uninterest_view(
    user_id: int = Depends(dependencies.CurrentUserId(user_type=users_constants.UserType.CLIENT)),
    uninterested_global_ids: list[str] = Body(...),
):
    """
    Удаление предпочтений пользователю
    """
    resources: dict[str, Any] = dict(
        user_repo=users_repos.UserRepo, property_repo=properties_repos.PropertyRepo
    )
    agents_users_interest: use_cases.UsersUninterestGlobalIdCase = use_cases.UsersUninterestGlobalIdCase(
        **resources
    )
    return await agents_users_interest(user_id=user_id, uninterested_global_ids=uninterested_global_ids)


@router.get(
    "/clients/fullname",
    status_code=HTTPStatus.OK,
    response_model=models.UserFullnameModel,
)
async def clients_users_fullname_view(
    client_id: int = Depends(dependencies.CurrentUserId(users_constants.UserType.CLIENT)),
):
    """
    Полное имя клиентов
    """
    resources: dict = dict(
        user_repo=users_repos.UserRepo,
        user_type=users_constants.UserType.CLIENT
    )
    users_fullname_case: use_cases.UsersFullnameCase = use_cases.UsersFullnameCase(**resources)
    return await users_fullname_case(user_id=client_id)


@router.get(
    "/clients/fullname_agent",
    status_code=HTTPStatus.OK,
    response_model=models.UserFullnameModel,
)
async def clients_agents_fullname_view(
    client_id: int = Depends(dependencies.CurrentUserId(users_constants.UserType.CLIENT)),
):
    """
    Полное имя клиентов
    """
    resources: dict = dict(
        user_repo=users_repos.UserRepo,
        user_type=users_constants.UserType.AGENT
    )
    agents_fullname_case: use_cases.AgentsFullnameByClientCase = use_cases.AgentsFullnameByClientCase(**resources)
    return await agents_fullname_case(user_id=client_id)


@router.patch(
    "/managers/interest",
    status_code=HTTPStatus.OK,
    response_model=models.ResponseUsersInterestModel,
    dependencies=[Depends(dependencies.DeletedUserCheck())],
)
async def manager_interest_view(
    interested: list[int] = Depends(
        dependencies.PropertiesFromGlobalId(properties_repos.PropertyRepo)
    ),
    user_id: int = Depends(dependencies.CurrentUserFromAmocrm(users_repos.UserRepo)),
):
    """
    Добавление предпочтений пользователем
    """
    resources: dict[str, Any] = dict(
        user_repo=users_repos.UserRepo,
        project_repo=projects_repos.ProjectRepo,
        property_repo=properties_repos.PropertyRepo,
        interests_repo=users_repos.InterestsRepo,
        agency_repo=agencies_repos.AgencyRepo,
    )
    users_interest_case: use_cases.UsersInterestCase = use_cases.UsersInterestCase(
        **resources
    )
    payload = models.RequestUsersInterestModel(interested=interested)
    return await users_interest_case(user_id=user_id, payload=payload)


@router.patch(
    "/managers/uninterests",
    status_code=HTTPStatus.OK,
    response_model=models.ResponseUsersUninterestModel,
    dependencies=[Depends(dependencies.DeletedUserCheck())],
)
async def managers_users_uninterest_view(
    uninterested: list[int] = Depends(
        dependencies.PropertiesFromGlobalId(properties_repos.PropertyRepo)
    ),
    user_id: int = Depends(dependencies.CurrentUserFromAmocrm(users_repos.UserRepo)),
):
    """
    Удаление предпочтений пользователю
    """
    resources: dict[str, Any] = dict(
        user_repo=users_repos.UserRepo, property_repo=properties_repos.PropertyRepo
    )
    agents_users_interest: use_cases.UsersUninterestCase = use_cases.UsersUninterestCase(
        **resources
    )
    payload = models.RequestUsersUninterestModel(uninterested=uninterested)
    return await agents_users_interest(user_id=user_id, payload=payload)


@router.get(
    "/agent/specs",
    status_code=HTTPStatus.OK,
    response_model=models.ResponseAgentsUsersSpecsModel,
    dependencies=[Depends(dependencies.DeletedUserCheck())],
)
async def agents_users_specs_view(
    specs: Callable[..., Coroutine] = Depends(filters.UserFilter.specs),
    agent_id: int = Depends(dependencies.CurrentUserId(user_type=users_constants.UserType.AGENT)),
):
    """
    Спеки пользователей агента
    """
    agents_users_specs = use_cases.AgentClientsSpecsCase()
    return await agents_users_specs(agent_id=agent_id, specs=specs)


@router.get(
    "/agent/facets",
    status_code=HTTPStatus.OK,
    response_model=models.ResponseAgentsUsersFacetsModel,
    dependencies=[Depends(dependencies.DeletedUserCheck())],
)
async def agents_users_facets_view(
    init_filters: dict[str, Any] = Depends(filters.UserFilter.filterize),
    facets: Callable[..., Coroutine] = Depends(filters.UserFilter.facets),
    agent_id: int = Depends(dependencies.CurrentUserId(user_type=users_constants.UserType.AGENT)),
):
    """
    Фасеты пользователей агента
    """
    resources: dict[str, Any] = dict(user_repo=users_repos.UserRepo)
    agents_users_facets = use_cases.AgentClientsFacetsCase(
        **resources
    )
    return await agents_users_facets(agent_id=agent_id, init_filters=init_filters, facets=facets)


@router.get(
    "/agent/lookup",
    status_code=HTTPStatus.OK,
    response_model=models.ResponseAgentsUsersLookupModel,
    dependencies=[Depends(dependencies.DeletedUserCheck())],
)
async def agents_users_lookup_view(
    lookup: str = Query(str(), alias="search"),
    init_filters: dict[str, Any] = Depends(filters.UserFilter.filterize),
    agent_id: int = Depends(dependencies.CurrentUserId(user_type=users_constants.UserType.AGENT)),
):
    """
    Поиск пользователя агента
    """
    resources: dict[str, Any] = dict(user_repo=users_repos.UserRepo)
    agents_users_search = use_cases.AgentClientsLookupCase(
        **resources
    )
    return await agents_users_search(agent_id=agent_id, lookup=lookup, init_filters=init_filters)


@router.post(
    "/client/unassign",
    status_code=HTTPStatus.OK,
    response_model_by_alias=True,
    response_model=models.ResponseUnassignClient
)
async def unassign_client_from_agent(
        token: str = Query(..., alias='t'), data: str = Query(..., alias='d')
):
    """Открепление клиента от агента"""
    resources: dict[str, Any] = dict(
        user_repo=users_repos.UserRepo,
        hasher=security.get_hasher,
    )
    get_agent_client_service = user_services.GetAgentClientFromQueryService(**resources)

    get_email_template_service: notification_services.GetEmailTemplateService = \
        notification_services.GetEmailTemplateService(
            email_template_repo=notifications_repos.EmailTemplateRepo,
        )
    resources: dict[str, Any] = dict(
        admin_repo=admins_repos.AdminRepo,
        email_class=email.EmailService,
        amocrm_class=amocrm.AmoCRM,
        sms_class=messages.SmsService,
        confirm_client_assign_repo=users_repos.ConfirmClientAssignRepo,
        get_email_template_service=get_email_template_service,
        get_agent_client_service=get_agent_client_service,
    )
    use_case: use_cases.UnassignCase = use_cases.UnassignCase(**resources)
    return await use_case(token=token, data=data)


@router.get(
    "/repres/specs",
    status_code=HTTPStatus.OK,
    response_model=models.ResponseRepresesUsersSpecsModel,
    dependencies=[
        Depends(dependencies.DeletedUserCheck()),
        Depends(dependencies.CurrentUserId(user_type=users_constants.UserType.REPRES)),
    ],
)
async def represes_users_specs_view(
    specs: Callable[..., Coroutine] = Depends(filters.UserFilter.specs),
    agency_id: int = Depends(dependencies.CurrentUserExtra(key="agency_id")),
):
    """
    Спеки пользователей представителя агентства
    """
    repres_users_specs = use_cases.RepresClientsSpecsCase()
    return await repres_users_specs(agency_id=agency_id, specs=specs)


@router.get(
    "/repres/facets",
    status_code=HTTPStatus.OK,
    response_model=models.ResponseRepresesUsersFacetsModel,
    dependencies=[
        Depends(dependencies.DeletedUserCheck()),
        Depends(dependencies.CurrentUserId(user_type=users_constants.UserType.REPRES)),
    ],
)
async def represes_users_facets_view(
    init_filters: dict[str, Any] = Depends(filters.UserFilter.filterize),
    facets: Callable[..., Coroutine] = Depends(filters.UserFilter.facets),
    agency_id: int = Depends(dependencies.CurrentUserExtra(key="agency_id")),
):
    """
    Фасеты пользователей представителя агентства
    """
    resources: dict[str, Any] = dict(user_repo=users_repos.UserRepo)
    repres_users_facets = use_cases.RepresClientsFacetsCase(
        **resources
    )
    return await repres_users_facets(
        agency_id=agency_id, init_filters=init_filters, facets=facets
    )


@router.post(
    "/repres/check",
    status_code=HTTPStatus.OK,
    response_model=models.ResponseUsersCheckModel,
    dependencies=[
        Depends(dependencies.DeletedUserCheck()),
        Depends(dependencies.CurrentUserId(user_type=users_constants.UserType.REPRES)),
    ],
)
async def represes_users_check_view(
    payload: models.RequestUsersCheckModel = Body(...),
    agency_id: int = Depends(dependencies.CurrentUserExtra(key="agency_id")),
):
    """
    Проверка пользователя на уникальность
    """
    resources: dict[str, Any] = dict(
        amocrm_class=amocrm.AmoCRM,
        user_repo=users_repos.UserRepo,
        check_repo=users_repos.CheckRepo,
        agent_repo=agents_repos.AgentRepo,
        amocrm_config=amocrm_config,
    )
    check_unique_service: user_services.CheckUniqueService = user_services.CheckUniqueService(**resources)

    get_email_template_service: notification_services.GetEmailTemplateService = \
        notification_services.GetEmailTemplateService(
            email_template_repo=notifications_repos.EmailTemplateRepo,
        )

    resources: dict[str, Any] = dict(
        user_repo=users_repos.UserRepo,
        check_repo=users_repos.CheckRepo,
        check_unique_service=check_unique_service,
        unique_status_repo=users_repos.UniqueStatusRepo,
        email_class=email.EmailService,
        get_email_template_service=get_email_template_service,
        booking_repo=booking_repos.BookingRepo,
        historical_dispute_repo=users_repos.HistoricalDisputeDataRepo,
    )
    repres_users_check: use_cases.UsersCheckCase = use_cases.UsersCheckCase(
        **resources
    )
    return await repres_users_check(agency_id=agency_id, payload=payload)


@router_v2.post(
    "/repres/check",
    status_code=HTTPStatus.OK,
    response_model=models.ResponseUsersCheckModel,
    dependencies=[
        Depends(dependencies.DeletedUserCheck()),
        Depends(dependencies.CurrentUserId(user_type=users_constants.UserType.REPRES)),
    ],
)
async def represes_users_check_view_v2(
    payload: models.RequestUsersCheckModel = Body(...),
    agency_id: int = Depends(dependencies.CurrentUserExtra(key="agency_id")),
):
    """
    Проверка пользователя на уникальность
    """
    resources: dict[str, Any] = dict(
        amocrm_class=amocrm.AmoCRM,
        user_repo=users_repos.UserRepo,
        check_repo=users_repos.CheckRepo,
        agent_repo=agents_repos.AgentRepo,
        check_term_repo=users_repos.CheckTermRepo,
        unique_status_repo=users_repos.UniqueStatusRepo,
        amocrm_config=amocrm_config,
    )
    check_unique_service: user_services.CheckUniqueServiceV2 = user_services.CheckUniqueServiceV2(**resources)

    get_email_template_service: notification_services.GetEmailTemplateService = \
        notification_services.GetEmailTemplateService(
            email_template_repo=notifications_repos.EmailTemplateRepo,
        )

    resources: dict[str, Any] = dict(
        user_repo=users_repos.UserRepo,
        check_repo=users_repos.CheckRepo,
        check_unique_service=check_unique_service,
        history_check_repo=users_repos.CheckHistoryRepo,
        unique_status_repo=users_repos.UniqueStatusRepo,
        email_class=email.EmailService,
        get_email_template_service=get_email_template_service,
        booking_repo=booking_repos.BookingRepo,
        historical_dispute_repo=users_repos.HistoricalDisputeDataRepo,
    )
    represes_users_check: use_cases.UsersCheckCase = use_cases.UsersCheckCase(
        **resources
    )
    return await represes_users_check(agency_id=agency_id, payload=payload)


@router.get(
    "/repres/lookup",
    status_code=HTTPStatus.OK,
    response_model=models.ResponseAgentsUsersLookupModel,
    dependencies=[
        Depends(dependencies.DeletedUserCheck()),
        Depends(dependencies.CurrentUserId(user_type=users_constants.UserType.REPRES)),
    ],
)
async def represes_users_lookup_view(
    lookup: str = Query(str(), alias="search"),
    init_filters: dict[str, Any] = Depends(filters.UserFilter.filterize),
    agency_id: int = Depends(dependencies.CurrentUserExtra(key="agency_id")),
):
    """
    Поиск пользователя представителя агентства
    """
    resources: dict[str, Any] = dict(user_repo=users_repos.UserRepo)
    repres_users_lookup = use_cases.RepresClientsLookupCase(
        **resources
    )
    return await repres_users_lookup(
        agency_id=agency_id, lookup=lookup, init_filters=init_filters
    )


@router.get(
    "/admin/specs",
    status_code=HTTPStatus.OK,
    response_model=models.ResponseAdminsUsersSpecsModel,
    dependencies=[Depends(dependencies.CurrentUserId(user_type=users_constants.UserType.ADMIN))],
)
async def admins_users_specs_view(
    specs: Callable[..., Coroutine] = Depends(filters.UserFilter.specs),
):
    """
    Спеки пользователей администратором
    """
    admins_users_specs = use_cases.AdminClientsSpecsCase()
    return await admins_users_specs(specs=specs)


@router.get(
    "/admin/facets",
    status_code=HTTPStatus.OK,
    response_model=models.ResponseAdminsUsersFacetsModel,
    dependencies=[Depends(dependencies.CurrentUserId(user_type=users_constants.UserType.ADMIN))],
)
async def admins_users_facets_views(
    init_filters: dict[str, Any] = Depends(filters.UserFilter.filterize),
    facets: Callable[..., Coroutine] = Depends(filters.UserFilter.facets),
):
    """
    Фасеты пользователей администратором
    """
    resources: dict[str, Any] = dict(user_repo=users_repos.UserRepo)
    admins_users_facets = use_cases.AdminClientsFacetsCase(
        **resources
    )
    return await admins_users_facets(init_filters=init_filters, facets=facets)


@router.get(
    "/admin/lookup",
    status_code=HTTPStatus.OK,
    response_model=models.ResponseAdminsUsersLookupModel,
    dependencies=[Depends(dependencies.CurrentUserId(user_type=users_constants.UserType.ADMIN))],
)
async def admins_users_lookup_view(
    lookup: str = Query(str(), alias="search"),
    init_filters: dict[str, Any] = Depends(filters.UserFilter.filterize),
):
    """
    Поиск пользователей администратором
    """
    resources: dict[str, Any] = dict(user_repo=users_repos.UserRepo)
    admins_users_lookup = use_cases.AdminClientsLookupCase(
        **resources
    )
    return await admins_users_lookup(lookup=lookup, init_filters=init_filters)


@router.post(
    "/admin/check/{user_id}/save_admin_comment",
    status_code=HTTPStatus.OK,
    response_model=models.ResponseAdminCommentModel,
)
async def admins_agents_users_dispute_comment_and_send_letter_view(
    payload: models.RequestAdminCommentModel = Body(...),
    admin_id=Depends(dependencies.CurrentUserId(user_type=users_constants.UserType.ADMIN))
):
    """
    Добавление комментария администратором при оспаривании решения уникальности
    """
    resources: dict = dict(
        agent_repo=agents_repos.AgentRepo,
        check_repo=users_repos.CheckRepo,
    )
    dispute_comment_and_send_letter: use_cases.AdminsAgentsDisputeCommendCase = (
        use_cases.AdminsAgentsDisputeCommendCase(**resources)
    )
    return await dispute_comment_and_send_letter(admin_id=admin_id, payload=payload)


@router.get(
    "/admin/history/checks",
    status_code=HTTPStatus.OK,
    response_model=models.ResponseAdminHistoryCheckListModel,
    dependencies=[Depends(dependencies.CurrentUserId(user_type=users_constants.UserType.ADMIN))],
)
async def admins_history_checks_view(
    pagination: paginations.PagePagination = Depends(dependencies.Pagination()),
    status_types: list[str] = Query([], description="Фильтры по статусам", alias='status_type'),
    init_filters: models.HistoryCheckSearchFilters = Depends()
):
    """
    История проверок уникальности для админа
    """
    resources: dict[str, Any] = dict(
        history_check_repo=users_repos.CheckHistoryRepo,
    )
    checks_history_case: use_cases.AdminChecksHistoryCase = use_cases.AdminChecksHistoryCase(**resources)

    return await checks_history_case(init_filters=init_filters, status_types=status_types, pagination=pagination)


@router.get(
    "/admin/history/specs",
    status_code=HTTPStatus.OK,
    response_model=models.AdminHistoryCheckSpecs,
    dependencies=[Depends(dependencies.CurrentUserId(user_type=users_constants.UserType.ADMIN))],
)
async def admins_history_checks_specs():
    """
    Спеки для истории проверок
    """
    return models.AdminHistoryCheckSpecs()


@router.get(
    "/agent",
    status_code=HTTPStatus.OK,
    response_model=models.ResponseAgentsUsersListModel,
    dependencies=[Depends(dependencies.DeletedUserCheck())],
    deprecated=True
)
async def agents_users_list_view(
    init_filters: dict[str, Any] = Depends(filters.UserFilter.filterize),
    pagination: paginations.PagePagination = Depends(dependencies.Pagination()),
    agent_id: int = Depends(dependencies.CurrentUserId(user_type=users_constants.UserType.AGENT)),
):
    """
    Пользователи агента
    УСТАРЕЛ. Вместо этого метода нужно использовать v2/agents
    """
    resources: dict[str, Any] = dict(
        user_repo=users_repos.UserRepo,
        user_type=users_constants.UserType.AGENT,
        check_repo=users_repos.CheckRepo,
        booking_repo=booking_repos.BookingRepo,
    )
    agents_users_list: use_cases.UsersListCase = use_cases.UsersListCase(**resources)
    return await agents_users_list(
        agent_id=agent_id, pagination=pagination, init_filters=init_filters
    )


@router.post(
    "/agent/check",
    status_code=HTTPStatus.OK,
    response_model=models.ResponseUsersCheckModel,
    dependencies=[Depends(dependencies.DeletedUserCheck())],
)
async def agents_users_check_view(
    payload: models.RequestUsersCheckModel = Body(...),
    agent_id: int = Depends(dependencies.CurrentUserId(user_type=users_constants.UserType.AGENT)),
):
    """
    Проверка пользователя на уникальность
    """
    resources: dict[str, Any] = dict(
        amocrm_class=amocrm.AmoCRM,
        user_repo=users_repos.UserRepo,
        check_repo=users_repos.CheckRepo,
        agent_repo=agents_repos.AgentRepo,
        history_check_repo=users_repos.CheckHistoryRepo,
        amocrm_config=amocrm_config,
    )
    check_unique_service: user_services.CheckUniqueService = user_services.CheckUniqueService(**resources)

    get_email_template_service: notification_services.GetEmailTemplateService = \
        notification_services.GetEmailTemplateService(
            email_template_repo=notifications_repos.EmailTemplateRepo,
        )

    resources: dict[str, Any] = dict(
        user_repo=users_repos.UserRepo,
        check_repo=users_repos.CheckRepo,
        check_unique_service=check_unique_service,
        unique_status_repo=users_repos.UniqueStatusRepo,
        email_class=email.EmailService,
        get_email_template_service=get_email_template_service,
        booking_repo=booking_repos.BookingRepo,
        historical_dispute_repo=users_repos.HistoricalDisputeDataRepo,
    )
    agents_users_check: use_cases.UsersCheckCase = use_cases.UsersCheckCase(**resources)
    return await agents_users_check(agent_id=agent_id, payload=payload)


@router_v2.post(
    "/agent/check",
    status_code=HTTPStatus.OK,
    response_model=models.ResponseUsersCheckModel,
    dependencies=[Depends(dependencies.DeletedUserCheck())],
)
async def agents_users_check_view_v2(
    payload: models.RequestUsersCheckModel = Body(...),
    agent_id: int = Depends(dependencies.CurrentUserId(user_type=users_constants.UserType.AGENT)),
):
    """
    Проверка пользователя на уникальность V2
    """
    resources: dict[str, Any] = dict(
        amocrm_class=amocrm.AmoCRM,
        user_repo=users_repos.UserRepo,
        check_repo=users_repos.CheckRepo,
        agent_repo=agents_repos.AgentRepo,
        check_term_repo=users_repos.CheckTermRepo,
        unique_status_repo=users_repos.UniqueStatusRepo,
        amocrm_config=amocrm_config,
    )
    check_unique_service: user_services.CheckUniqueServiceV2 = user_services.CheckUniqueServiceV2(**resources)

    get_email_template_service: notification_services.GetEmailTemplateService = \
        notification_services.GetEmailTemplateService(
            email_template_repo=notifications_repos.EmailTemplateRepo,
        )

    resources: dict[str, Any] = dict(
        user_repo=users_repos.UserRepo,
        check_repo=users_repos.CheckRepo,
        check_unique_service=check_unique_service,
        history_check_repo=users_repos.CheckHistoryRepo,
        unique_status_repo=users_repos.UniqueStatusRepo,
        email_class=email.EmailService,
        get_email_template_service=get_email_template_service,
        booking_repo=booking_repos.BookingRepo,
        historical_dispute_repo=users_repos.HistoricalDisputeDataRepo,
    )
    agents_users_check: use_cases.UsersCheckCase = use_cases.UsersCheckCase(**resources)
    return await agents_users_check(agent_id=agent_id, payload=payload)


@router.patch(
    "/agent/check-dispute",
    status_code=HTTPStatus.OK,
    response_model=models.ResponseAgentUsersCheckDisputeModel,
)
async def agents_users_check_dispute_view(
    payload: models.RequestAgentsUsersCheckDisputeModel = Body(...),
    agent_id: int = Depends(dependencies.CurrentUserId(user_type=users_constants.UserType.AGENT)),
):
    """
    Оспаривание результатов проверки агентом
    """
    get_email_template_service: notification_services.GetEmailTemplateService = \
        notification_services.GetEmailTemplateService(
            email_template_repo=notifications_repos.EmailTemplateRepo,
        )
    resources: dict = dict(
        check_repo=users_repos.CheckRepo,
        email_class=email.EmailService,
        agent_repo=agents_repos.AgentRepo,
        user_repo=users_repos.UserRepo,
        admin_repo=admins_repos.AdminRepo,
        email_recipients=email_recipients_config,
        get_email_template_service=get_email_template_service,
        unique_status_repo=users_repos.UniqueStatusRepo,
        historical_dispute_repo=users_repos.HistoricalDisputeDataRepo,
    )

    agents_users_check_dispute: use_cases.CheckDisputeCase = use_cases.CheckDisputeCase(**resources)
    return await agents_users_check_dispute(dispute_agent_id=agent_id, payload=payload)


@router.patch(
    "/repres/check-dispute",
    status_code=HTTPStatus.OK,
    response_model=models.ResponseAgentUsersCheckDisputeModel,
)
async def agents_users_check_dispute_view(
    payload: models.RequestAgentsUsersCheckDisputeModel = Body(...),
    repres_id: int = Depends(dependencies.CurrentUserId(user_type=users_constants.UserType.REPRES)),
):
    """
    Оспаривание результатов проверки представителем
    """
    get_email_template_service: notification_services.GetEmailTemplateService = \
        notification_services.GetEmailTemplateService(
            email_template_repo=notifications_repos.EmailTemplateRepo,
        )
    resources: dict = dict(
        check_repo=users_repos.CheckRepo,
        email_class=email.EmailService,
        repres_repo=represes_repos.RepresRepo,
        user_repo=users_repos.UserRepo,
        admin_repo=admins_repos.AdminRepo,
        email_recipients=email_recipients_config,
        get_email_template_service=get_email_template_service,
        unique_status_repo=users_repos.UniqueStatusRepo,
        historical_dispute_repo=users_repos.HistoricalDisputeDataRepo,
    )

    agents_users_check_dispute: use_cases.RepresCheckDisputeCase = use_cases.RepresCheckDisputeCase(**resources)
    return await agents_users_check_dispute(dispute_repres_id=repres_id, payload=payload)


@router.patch(
    "/agent/interest/{user_id}",
    status_code=HTTPStatus.OK,
    response_model=models.ResponseUsersInterestModel,
    dependencies=[Depends(dependencies.DeletedUserCheck())],
)
async def agents_users_interest_view(
    user_id: int = Path(...),
    payload: models.RequestUsersInterestModel = Body(...),
    agent_id: int = Depends(dependencies.CurrentUserId(user_type=users_constants.UserType.AGENT)),
):
    """
    Добавление предпочтений пользователю
    """
    resources: dict[str, Any] = dict(
        user_repo=users_repos.UserRepo,
        project_repo=projects_repos.ProjectRepo,
        property_repo=properties_repos.PropertyRepo,
        interests_repo=users_repos.InterestsRepo,
        agency_repo=agencies_repos.AgencyRepo,
    )
    users_interest_case: use_cases.UsersInterestCase = use_cases.UsersInterestCase(
        **resources
    )
    return await users_interest_case(user_id=user_id, agent_id=agent_id, payload=payload)


@router.patch(
    "/agent/uninterest/{user_id}",
    status_code=HTTPStatus.OK,
    response_model=models.ResponseUsersUninterestModel,
    dependencies=[Depends(dependencies.DeletedUserCheck())],
)
async def agents_users_uninterest_view(
    user_id: int = Path(...),
    payload: models.RequestUsersUninterestModel = Body(...),
    agent_id: int = Depends(dependencies.CurrentUserId(user_type=users_constants.UserType.AGENT)),
):
    """
    Удаление предпочтений пользователю
    """
    resources: dict[str, Any] = dict(
        user_repo=users_repos.UserRepo, property_repo=properties_repos.PropertyRepo
    )
    agents_users_interest: use_cases.UsersUninterestCase = use_cases.UsersUninterestCase(
        **resources
    )
    return await agents_users_interest(user_id=user_id, agent_id=agent_id, payload=payload)


@router.patch(
    "/agent/unbound/{user_id}",
    status_code=HTTPStatus.NO_CONTENT,
    dependencies=[Depends(dependencies.DeletedUserCheck())],
)
async def agents_users_unbound_view(
    user_id: int = Path(...),
    agent_id: int = Depends(dependencies.CurrentUserId(user_type=users_constants.UserType.AGENT)),
):
    """
    Отвязка пользователя агента
    """
    resources: dict[str, Any] = dict(
        user_repo=users_repos.UserRepo,
        check_repo=users_repos.CheckRepo,
        booking_repo=booking_repos.BookingRepo,
    )
    agents_users_unbound: use_cases.AgentsUsersUnboundCase = use_cases.AgentsUsersUnboundCase(
        **resources
    )
    return await agents_users_unbound(agent_id=agent_id, user_id=user_id)


@router.post(
    "/agent/assign_client",
    status_code=HTTPStatus.OK,
    dependencies=[Depends(dependencies.DeletedUserCheck())],
    response_model=models.ResponseAssignClient,
    response_model_by_alias=False
)
async def assign_client_to_agent(
    agent_id: int = Depends(dependencies.CurrentUserId(user_type=users_constants.UserType.AGENT)),
    payload: models.RequestAssignClient = Body(...),
    request: Request = Request,
):
    """Закрепить клиента за агентом"""
    resources: dict[str, Any] = dict(
        booking_repo=booking_repos.BookingRepo,
        task_instance_repo=task_management_repos.TaskInstanceRepo,
        task_chain_repo=task_management_repos.TaskChainRepo,
        task_status_repo=task_management_repos.TaskStatusRepo,
    )
    create_task_instance_service = task_management_services.CreateTaskInstanceService(
        **resources
    )
    get_email_template_service: notification_services.GetEmailTemplateService = \
        notification_services.GetEmailTemplateService(
            email_template_repo=notifications_repos.EmailTemplateRepo,
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
        user_repo=users_repos.UserRepo,
        check_repo=users_repos.CheckRepo,
        project_repo=projects_repos.ProjectRepo,
        booking_repo=booking_repos.BookingRepo,
        amo_statuses_repo=amocrm_repos.AmoStatusesRepo,
        template_repo=notifications_repos.AssignClientTemplateRepo,
        amocrm_config=amocrm_config,
        email_class=email.EmailService,
        amocrm_class=amocrm.AmoCRM,
        sms_class=messages.SmsService,
        hasher=security.get_hasher,
        site_config=site_config,
        request=request,
        get_email_template_service=get_email_template_service,
        create_task_instance_service=create_task_instance_service,
        confirm_client_assign_repo=users_repos.ConfirmClientAssignRepo,
        check_pinning=check_pinning,
    )
    use_case: use_cases.AssignClientCase = use_cases.AssignClientCase(**resources)
    return await use_case(payload=payload, agent_id=agent_id)


@router.post(
    "/repres/assign_client",
    status_code=HTTPStatus.OK,
    dependencies=[Depends(dependencies.DeletedUserCheck())],
    response_model=models.ResponseAssignClient,
    response_model_by_alias=False
)
async def assign_client_to_repres(
    repres_id: int = Depends(dependencies.CurrentUserId(user_type=users_constants.UserType.REPRES)),
    payload: models.RequestAssignClient = Body(...),
    request: Request = Request,
):
    """Закрепить клиента за представителем агентства"""
    resources: dict[str, Any] = dict(
        booking_repo=booking_repos.BookingRepo,
        task_instance_repo=task_management_repos.TaskInstanceRepo,
        task_chain_repo=task_management_repos.TaskChainRepo,
        task_status_repo=task_management_repos.TaskStatusRepo,
    )
    create_task_instance_service = task_management_services.CreateTaskInstanceService(
        **resources
    )
    get_email_template_service: notification_services.GetEmailTemplateService = \
        notification_services.GetEmailTemplateService(
            email_template_repo=notifications_repos.EmailTemplateRepo,
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
        user_repo=users_repos.UserRepo,
        check_repo=users_repos.CheckRepo,
        project_repo=projects_repos.ProjectRepo,
        booking_repo=booking_repos.BookingRepo,
        amo_statuses_repo=amocrm_repos.AmoStatusesRepo,
        template_repo=notifications_repos.AssignClientTemplateRepo,
        amocrm_config=amocrm_config,
        email_class=email.EmailService,
        amocrm_class=amocrm.AmoCRM,
        sms_class=messages.SmsService,
        hasher=security.get_hasher,
        site_config=site_config,
        request=request,
        create_task_instance_service=create_task_instance_service,
        confirm_client_assign_repo=users_repos.ConfirmClientAssignRepo,
        get_email_template_service=get_email_template_service,
        check_pinning=check_pinning,
    )
    use_case: use_cases.AssignClientCase = use_cases.AssignClientCase(**resources)
    return await use_case(payload=payload, repres_id=repres_id)


@router.post(
    "/client/assign",
    status_code=HTTPStatus.OK,
    dependencies=[Depends(dependencies.DeletedUserCheck())],
)
async def confirm_assign_client(
    token: str = Query(..., alias='t'), data: str = Query(..., alias='d')
):
    """Подтвердить закрепление клиента за агентом"""
    resources: dict[str, Any] = dict(
        user_repo=users_repos.UserRepo,
        hasher=security.get_hasher,
    )
    get_agent_client_service = user_services.GetAgentClientFromQueryService(**resources)

    resources: dict[str, Any] = dict(
        confirm_client_assign_repo=users_repos.ConfirmClientAssignRepo,
        get_agent_client_service=get_agent_client_service,
    )
    use_case: use_cases.ConfirmAssignClientCase = use_cases.ConfirmAssignClientCase(
        **resources
    )
    await use_case(token=token, data=data)


@router.get(
    "/repres",
    status_code=HTTPStatus.OK,
    response_model=models.ResponseRepresesUsersListModel,
    dependencies=[
        Depends(dependencies.DeletedUserCheck()),
        Depends(dependencies.CurrentUserId(user_type=users_constants.UserType.REPRES)),
    ],
    deprecated=True
)
async def represes_users_list_view(
    init_filters: dict[str, Any] = Depends(filters.UserFilter.filterize),
    agency_id: int = Depends(dependencies.CurrentUserExtra(key="agency_id")),
    pagination: paginations.PagePagination = Depends(dependencies.Pagination()),
):
    """
    Пользователи представителя агентства
    """
    resources: dict[str, Any] = dict(
        user_repo=users_repos.UserRepo,
        check_repo=users_repos.CheckRepo,
        booking_repo=booking_repos.BookingRepo,
        user_type=users_constants.UserType.REPRES
    )
    represes_users_list: use_cases.UsersListCase = use_cases.UsersListCase(
        **resources
    )
    return await represes_users_list(agency_id=agency_id, init_filters=init_filters, pagination=pagination)


@router.patch(
    "/repres/interest/{user_id}",
    status_code=HTTPStatus.OK,
    response_model=models.ResponseUsersInterestModel,
    dependencies=[
        Depends(dependencies.DeletedUserCheck()),
        Depends(dependencies.CurrentUserId(user_type=users_constants.UserType.REPRES)),
    ],
)
async def represes_users_interest_view(
    user_id: int = Path(...),
    payload: models.RequestUsersInterestModel = Body(...),
    agency_id: int = Depends(dependencies.CurrentUserExtra(key="agency_id")),
):
    """
    Добавление предпочтений пользователю представителем агентства
    """
    resources: dict[str, Any] = dict(
        user_repo=users_repos.UserRepo,
        project_repo=projects_repos.ProjectRepo,
        property_repo=properties_repos.PropertyRepo,
        interests_repo=users_repos.InterestsRepo,
        agency_repo=agencies_repos.AgencyRepo,
    )
    users_interest_case: use_cases.UsersInterestCase = (
        use_cases.UsersInterestCase(**resources)
    )
    return await users_interest_case(user_id=user_id, agency_id=agency_id, payload=payload)


@router.patch(
    "/repres/uninterest/{user_id}",
    status_code=HTTPStatus.OK,
    response_model=models.ResponseUsersUninterestModel,
    dependencies=[
        Depends(dependencies.DeletedUserCheck()),
        Depends(dependencies.CurrentUserId(user_type=users_constants.UserType.REPRES)),
    ],
)
async def represes_users_uninterest_view(
    user_id: int = Path(...),
    payload: models.RequestUsersUninterestModel = Body(...),
    agency_id: int = Depends(dependencies.CurrentUserExtra(key="agency_id")),
):
    """
    Удаление предпочтений пользователю
    """
    resources: dict[str, Any] = dict(
        user_repo=users_repos.UserRepo, property_repo=properties_repos.PropertyRepo
    )
    represes_users_interest: use_cases.UsersUninterestCase = (
        use_cases.UsersUninterestCase(**resources)
    )
    return await represes_users_interest(user_id=user_id, agency_id=agency_id, payload=payload)


@router.patch(
    "/repres/bound/{user_id}",
    status_code=HTTPStatus.NO_CONTENT,
    dependencies=[
        Depends(dependencies.DeletedUserCheck()),
        Depends(dependencies.CurrentUserId(user_type=users_constants.UserType.REPRES)),
    ],
)
async def represes_users_bound_view(
    user_id: int = Path(...),
    payload: models.RequestRepresesUsersBoundModel = Body(...),
    agency_id: int = Depends(dependencies.CurrentUserExtra(key="agency_id")),
):
    """
    Привязка пользователя представителем агентства
    """
    resources: dict[str, Any] = dict(
        user_repo=users_repos.UserRepo,
        check_repo=users_repos.CheckRepo,
        agent_repo=agents_repos.AgentRepo,
        booking_repo=booking_repos.BookingRepo,
        change_client_agent_task=users_tasks.change_client_agent_task,
    )
    repres_users_bound: use_cases.RepresesUsersBoundCase = use_cases.RepresesUsersBoundCase(
        **resources
    )
    return await repres_users_bound(agency_id=agency_id, user_id=user_id, payload=payload)


@router.patch(
    "/repres/unbound/{user_id}",
    status_code=HTTPStatus.NO_CONTENT,
    dependencies=[
        Depends(dependencies.DeletedUserCheck()),
        Depends(dependencies.CurrentUserId(user_type=users_constants.UserType.REPRES)),
    ],
)
async def represes_users_unbound_view(
    user_id: int = Path(...),
    payload: models.RequestRepresesUsersUnboundModel = Body(...),
    agency_id: int = Depends(dependencies.CurrentUserExtra(key="agency_id")),
):
    """
    Отвязка пользователя представителем агентства
    """
    resources: dict[str, Any] = dict(
        user_repo=users_repos.UserRepo,
        check_repo=users_repos.CheckRepo,
        agent_repo=agents_repos.AgentRepo,
        booking_repo=booking_repos.BookingRepo,
    )
    repres_users_unbound: use_cases.RepresesUsersUnboundCase = use_cases.RepresesUsersUnboundCase(
        **resources
    )
    return await repres_users_unbound(agency_id=agency_id, user_id=user_id, payload=payload)


@router.patch(
    "/repres/rebound/{user_id}",
    status_code=HTTPStatus.NO_CONTENT,
    dependencies=[
        Depends(dependencies.DeletedUserCheck()),
        Depends(dependencies.CurrentUserId(user_type=users_constants.UserType.REPRES)),
    ],
)
async def represes_users_rebound_view(
    user_id: int = Path(...),
    payload: models.RequestRepresesUsersReboundModel = Body(...),
    agency_id: int = Depends(dependencies.CurrentUserExtra(key="agency_id")),
):
    """
    Перепривязка пользователя представителем агентства
    """
    resources: dict[str, Any] = dict(
        amocrm_config=amocrm_config,
        amocrm_class=amocrm.AmoCRM,
        user_repo=users_repos.UserRepo,
        agent_repo=agents_repos.AgentRepo,
    )
    change_agent_service: user_services.ChangeAgentService = user_services.ChangeAgentService(**resources)
    resources: dict[str, Any] = dict(
        user_repo=users_repos.UserRepo,
        check_repo=users_repos.CheckRepo,
        agent_repo=agents_repos.AgentRepo,
        booking_repo=booking_repos.BookingRepo,
        change_agent_service=change_agent_service,
    )
    represes_users_rebound_case: use_cases.RepresesUsersReboundCase = (
        use_cases.RepresesUsersReboundCase(**resources)
    )
    return await represes_users_rebound_case(user_id=user_id, payload=payload, agency_id=agency_id)



@router.get(
    "/admin",
    status_code=HTTPStatus.OK,
    response_model=models.ResponseAdminsUsersListModel,
    dependencies=[Depends(dependencies.CurrentUserId(user_type=users_constants.UserType.ADMIN))],
    deprecated=True
)
async def admins_users_list_view(
    init_filters: dict[str, Any] = Depends(filters.UserFilter.filterize),
    pagination: paginations.PagePagination = Depends(dependencies.Pagination()),
):
    """
    Сделки администратором
    """
    resources: dict[str, Any] = dict(
        user_repo=users_repos.UserRepo,
        check_repo=users_repos.CheckRepo,
        booking_repo=booking_repos.BookingRepo,
        user_type=users_constants.UserType.ADMIN
    )
    admins_users_list: use_cases.UsersListCase = use_cases.UsersListCase(**resources)
    return await admins_users_list(pagination=pagination, init_filters=init_filters)


@router.post(
    "/admin/dispute/{user_id}",
    status_code=HTTPStatus.OK,
    response_model=models.ResponseAdminsUserCheckDispute,
    dependencies=[Depends(dependencies.CurrentUserId(user_type=users_constants.UserType.ADMIN))]
)
async def admins_resolve_user_dispute(
    user_id: int = Path(...),
    payload: models.RequestAdminsUserCheckDispute = Body(...)
):
    """Поставить статус проверки клиента администратором."""
    get_email_template_service: notification_services.GetEmailTemplateService = \
        notification_services.GetEmailTemplateService(
            email_template_repo=notifications_repos.EmailTemplateRepo,
        )
    resources: dict[str, Any] = dict(
        user_repo=users_repos.UserRepo,
        check_repo=users_repos.CheckRepo,
        email_class=email.EmailService,
        agent_repo=agents_repos.AgentRepo,
        get_email_template_service=get_email_template_service,
    )
    resolve_user_dispute: use_cases.ResolveDisputeCase = use_cases.ResolveDisputeCase(
        **resources
    )
    return await resolve_user_dispute(user_id, payload)


@router.post(
    "/check_user_contacts",
    status_code=HTTPStatus.OK,
    response_model=models.ResponseUserCheckUnique,
)
async def check_user_contacts(
    payload: models.RequestUserCheckUnique = Body(...)
):
    """
    Проверка уникальности пользователя в базе по телефону и почте и валидация телефона и почты пользователя.
    """
    check_user_unique_service: user_services.UserCheckUniqueService = user_services.UserCheckUniqueService(
        user_repo=users_repos.UserRepo,
    )
    check_user_contact_case: use_cases.UserCheckUniqueCase = use_cases.UserCheckUniqueCase(
        check_user_unique_service=check_user_unique_service
    )
    return await check_user_contact_case(payload=payload)


@router.patch(
    "/superuser/fill/{user_id}",
    status_code=HTTPStatus.OK,
)
def superuser_users_fill_data_view(
    user_id: int = Path(...),
    data: str = Query(...),
):
    """
    Обновление данные пользователя в АмоСРМ после изменения в админке брокера.
    """
    superuser_user_fill_data_case: use_cases.SuperuserUserFillDataCase = use_cases.SuperuserUserFillDataCase(
        export_user_in_amo_task=users_tasks.export_user_in_amo,
    )
    return superuser_user_fill_data_case(user_id=user_id, data=data)


@router.post(
    "/reset_password",
    status_code=HTTPStatus.NO_CONTENT,
    summary="Смена пароля через почту"
)
async def email_reset_view(payload: models.RequestEmailResetModel = Body(...)):
    """
    Ссылка для сброса пароля через почту.
    Используется для кнопки "забыли пароль" для агентов, представителей и админов.
    """
    get_email_template_service: notification_services.GetEmailTemplateService = \
        notification_services.GetEmailTemplateService(
            email_template_repo=notifications_repos.EmailTemplateRepo,
        )
    resources: dict[str, Any] = dict(
        site_config=site_config,
        email_class=email.EmailService,
        user_repo=users_repos.UserRepo,
        token_creator=security.create_email_token,
        get_email_template_service=get_email_template_service,
    )
    email_reset: use_cases.EmailResetCase = use_cases.EmailResetCase(**resources)
    return await email_reset(payload=payload)


@router.post(
    "/ticket",
    status_code=HTTPStatus.CREATED,
    dependencies=[Depends(dependencies.CurrentAnyTypeUserId())],
)
async def create_ticket(
    payload: models.RequestCreateTicket = Body(...),
):
    """
    Создание заявки.
    """
    resources: dict[str, Any] = dict(
        ticket_repo=dashboard_repos.TicketRepo,
        city_repo=cities_repos.CityRepo,
    )
    create_ticket_case: dashboard_use_cases.CreateTicketCase = dashboard_use_cases.CreateTicketCase(**resources)
    return await create_ticket_case(payload=payload)
