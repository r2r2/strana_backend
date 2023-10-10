from uuid import UUID
from typing import Any, Callable, Coroutine, Optional

import tortoise
from fastapi import (
    APIRouter,
    Body,
    Depends,
    File,
    Path,
    Query,
    Request,
    Response,
    UploadFile,
)
from fastapi.responses import RedirectResponse
from http import HTTPStatus

from common import (
    amocrm,
    dependencies,
    email,
    messages,
    paginations,
    redis,
    security,
    utils,
)
from common.amocrm.services import BindContactCompanyService
from common.amocrm.tasks import bind_contact_to_company
from config import (
    auth_config,
    redis_config,
    session_config,
    site_config,
    tortoise_config,
)
from src.admins import repos as admin_repos
from src.agencies import repos as agencies_repos
from src.agents import filters, models
from src.agents import services
from src.agents import tasks as agents_tasks
from src.agents import use_cases
from src.booking import constants as booking_constants
from src.questionnaire import repos as questionnaire_repos
from src.task_management.factories import UpdateTaskInstanceStatusServiceFactory
from src.users import constants as users_constants
from src.users import use_cases as users_cases
from src.users.filters import BookingUserFilter
from src.users import services as user_services
from src.notifications import services as notification_services
from src.notifications import repos as notification_repos
from src.agents import repos as agents_repos
from src.users import repos as users_repos
from src.booking import repos as booking_repos

router = APIRouter(prefix="/agents", tags=["Agents"])


@router.post(
    "/register",
    status_code=HTTPStatus.CREATED,
    response_model=models.ResponseProcessRegisterModel,
)
async def process_register_view(
    payload: models.RequestProcessRegisterModel = Body(...),
):
    """
    Регистрация агента
    """
    create_contact_service = services.CreateContactService(
        amocrm_class=amocrm.AmoCRM,
        agent_repo=agents_repos.AgentRepo,
        agency_repo=agencies_repos.AgencyRepo,
    )
    ensure_broker_tag_service = services.EnsureBrokerTagService(
        amocrm_class=amocrm.AmoCRM,
        agent_repo=agents_repos.AgentRepo,
    )
    get_email_template_service: notification_services.GetEmailTemplateService = (
        notification_services.GetEmailTemplateService(
            email_template_repo=notification_repos.EmailTemplateRepo,
        )
    )
    check_user_unique_service: user_services.UserCheckUniqueService = (
        user_services.UserCheckUniqueService(
            user_repo=users_repos.UserRepo,
        )
    )
    resources: dict[str:Any] = dict(
        amocrm_class=amocrm.AmoCRM,
        orm_class=tortoise.Tortoise,
        orm_config=tortoise_config,
    )
    bind_contact_to_company_service: BindContactCompanyService = (
        BindContactCompanyService(**resources)
    )
    resources: dict[str, Any] = dict(
        site_config=site_config,
        hasher=security.get_hasher,
        email_class=email.EmailService,
        agent_repo=agents_repos.AgentRepo,
        agency_repo=agencies_repos.AgencyRepo,
        user_type=users_constants.UserType.AGENT,
        token_creator=security.create_email_token,
        import_clients_task=agents_tasks.import_clients_task,
        create_contact_service=create_contact_service,
        ensure_broker_tag_service=ensure_broker_tag_service,
        bind_contact_to_company_service=bind_contact_to_company_service,
        check_user_unique_service=check_user_unique_service,
        get_email_template_service=get_email_template_service,
        user_role_repo=users_repos.UserRoleRepo,
    )
    process_register: use_cases.ProcessRegisterCase = use_cases.ProcessRegisterCase(
        **resources
    )
    return await process_register(payload=payload)


@router.get("/confirm_email", status_code=HTTPStatus.PERMANENT_REDIRECT)
async def confirm_email_view(
    token: str = Query(..., alias="q"), email_token: str = Query(..., alias="p")
):
    """
    Служебный ендпоинт для подтверждения почты
    """
    resources: dict[str, Any] = dict(
        site_config=site_config,
        agent_repo=agents_repos.AgentRepo,
        user_type=users_constants.UserType.AGENT,
        admin_user_type=users_constants.UserType.ADMIN,
        token_decoder=security.decode_email_token,
        admin_repo=admin_repos.AdminRepo,
        email_class=email.EmailService,
    )
    confirm_email: use_cases.ConfirmEmailCase = use_cases.ConfirmEmailCase(**resources)
    return RedirectResponse(
        url=await confirm_email(token=token, email_token=email_token)
    )


@router.post(
    "/resend_email_verification",
    status_code=HTTPStatus.OK,
    summary="Отправка письма на подтверждение почты",
)
async def resend_confirm_letter_view(
    agent_id: Optional[int] = Depends(
        dependencies.CurrentUserId(user_type=users_constants.UserType.AGENT)
    ),
):
    """Отправляет письмо подвтерждения на почту агенту."""
    # возможно, необходимо добавить cooldown-таймер
    get_email_template_service: notification_services.GetEmailTemplateService = (
        notification_services.GetEmailTemplateService(
            email_template_repo=notification_repos.EmailTemplateRepo,
        )
    )
    resources: dict[str, Any] = dict(
        site_config=site_config,
        email_class=email.EmailService,
        agent_repo=agents_repos.AgentRepo,
        token_creator=security.create_email_token,
        get_email_template_service=get_email_template_service,
    )
    resend_letter: use_cases.AgentResendLetterCase = use_cases.AgentResendLetterCase(
        **resources
    )
    return await resend_letter(agent_id)


@router.get("/confirm_phone", status_code=HTTPStatus.PERMANENT_REDIRECT)
async def confirm_phone_view(
    token: str = Query(..., alias="q"), phone_token: str = Query(..., alias="p")
):
    """
    Служебный ендпоинт для подтверждения телефона
    """
    resources: dict[str, Any] = dict(
        site_config=site_config,
        agent_repo=agents_repos.AgentRepo,
        user_type=users_constants.UserType.AGENT,
        token_decoder=security.decode_email_token,
    )
    confirm_phone: use_cases.ConfirmPhoneCase = use_cases.ConfirmPhoneCase(**resources)
    return RedirectResponse(
        url=await confirm_phone(token=token, phone_token=phone_token)
    )


@router.get("/reset_password", status_code=HTTPStatus.PERMANENT_REDIRECT)
async def reset_password_view(
    request: Request,
    token: str = Query(..., alias="q"),
    discard_token: str = Query(..., alias="p"),
):
    """
    Служебный ендпоинт для сброса пароля
    """
    resources: dict[str, Any] = dict(
        site_config=site_config,
        auth_config=auth_config,
        session=request.session,
        session_config=session_config,
        agent_repo=agents_repos.AgentRepo,
        user_type=users_constants.UserType.AGENT,
        token_decoder=security.decode_email_token,
    )
    reset_password: use_cases.ResetPasswordCase = use_cases.ResetPasswordCase(
        **resources
    )
    return RedirectResponse(
        url=await reset_password(token=token, discard_token=discard_token)
    )


@router.get(
    "/reset_available",
    status_code=HTTPStatus.OK,
    response_model=models.ResponseResetAvailableModel,
    deprecated=True,
)
async def reset_available_view(request: Request):
    """
    Доступность сброса пароля
    """
    resources: dict[str, Any] = dict(
        session=request.session,
        session_config=session_config,
        agent_repo=agents_repos.AgentRepo,
        user_type=users_constants.UserType.AGENT,
    )
    reset_available: use_cases.ResetAvailableCase = use_cases.ResetAvailableCase(
        **resources
    )
    return await reset_available()


@router.patch("/change_password", status_code=HTTPStatus.OK, summary="Смена пароля")
async def change_password_view(
    request: Request,
    payload: models.RequestChangePasswordModel = Body(...),
    agent_id: Optional[int] = Depends(
        dependencies.CurrentUserId(user_type=users_constants.UserType.AGENT)
    ),
):
    """
    API метод для смены пароля Агента
    """
    resources: dict[str, Any] = dict(
        session=request.session,
        hasher=security.get_hasher,
        session_config=session_config,
        user_repo=agents_repos.AgentRepo,
        user_type=users_constants.UserType.AGENT,
    )
    change_password: users_cases.ChangePasswordCase = users_cases.ChangePasswordCase(
        **resources
    )
    return await change_password(user_id=agent_id, payload=payload)


@router.post(
    "/set_password",
    status_code=HTTPStatus.OK,
    response_model=models.ResponseSetPasswordModel,
    summary="Установка пароля",
)
async def set_password_view(
    request: Request, payload: models.RequestSetPasswordModel = Body(...)
):
    """
    Установка пароля для агентов созданных представителем
    """
    get_email_template_service: notification_services.GetEmailTemplateService = (
        notification_services.GetEmailTemplateService(
            email_template_repo=notification_repos.EmailTemplateRepo,
        )
    )
    resources: dict[str, Any] = dict(
        session=request.session,
        site_config=site_config,
        hasher=security.get_hasher,
        session_config=session_config,
        email_class=email.EmailService,
        agent_repo=agents_repos.AgentRepo,
        user_type=users_constants.UserType.AGENT,
        token_creator=security.create_email_token,
        get_email_template_service=get_email_template_service,
    )
    set_password: use_cases.SetPasswordCase = use_cases.SetPasswordCase(**resources)
    return await set_password(payload=payload)


@router.post(
    "/login",
    status_code=HTTPStatus.OK,
    response_model=models.ResponseProcessLoginModel,
    summary="Логин",
)
async def process_login_view(
    request: Request, payload: models.RequestProcessLoginModel = Body(...)
):
    """
    API метод для входа в акканут
    """
    handler: users_cases.UserAgencyHandler = users_cases.UserAgencyHandler()
    handler.set_next(None)

    resources: dict[str, Any] = dict(
        auth_config=auth_config,
        session=request.session,
        hasher=security.get_hasher,
        login_handler=handler,
        session_config=session_config,
        user_repo=agents_repos.AgentRepo,
        user_type=users_constants.UserType.AGENT,
        token_creator=security.create_access_token,
    )
    process_login: use_cases.ProcessLoginCase = use_cases.ProcessLoginCase(**resources)
    return await process_login(payload=payload)


@router.get(
    "/me",
    status_code=HTTPStatus.OK,
    response_model=models.ResponseGetMeModel,
    summary="Информация об агенте",
)
async def get_me_view(
    agent_id: int = Depends(
        dependencies.CurrentUserId(user_type=users_constants.UserType.AGENT)
    ),
):
    """
    Получение текущего агента
    """
    resources: dict[str, Any] = dict(agent_repo=agents_repos.AgentRepo)
    get_me: use_cases.GetMeCase = use_cases.GetMeCase(**resources)
    return await get_me(agent_id=agent_id)


@router.get(
    "/profile",
    status_code=HTTPStatus.OK,
    response_model=models.ResponseProfileModel,
    summary="Профиль агента",
)
async def get_profile_view(
    agent_id: int = Depends(
        dependencies.CurrentUserId(user_type=users_constants.UserType.AGENT)
    ),
):
    """
    API метод для получения профиля текущего агента
    """
    resources: dict[str, Any] = dict(agent_repo=agents_repos.AgentRepo)
    get_me: use_cases.GetMeCase = use_cases.GetMeCase(**resources)
    return await get_me(agent_id=agent_id)


@router.patch(
    "/profile",
    status_code=HTTPStatus.OK,
    response_model=models.ResponseProfileModel,
    summary="Изменение профиля агента",
)
async def update_profile_view(
    agent_id: int = Depends(
        dependencies.CurrentUserId(user_type=users_constants.UserType.AGENT)
    ),
    payload: models.UpdateProfileModel = Body(...),
):
    """
    API метод для обновления персональных данных агента
    """
    resources = dict(
        agent_repo=agents_repos.AgentRepo,
        user_type=users_constants.UserType.AGENT,
        amocrm_class=amocrm.AmoCRM,
    )
    update_me: use_cases.UpdateProfileCase = use_cases.UpdateProfileCase(**resources)
    return await update_me(agent_id=agent_id, payload=payload)


@router.get(
    "/session_token",
    status_code=HTTPStatus.OK,
    response_model=models.ResponseSessionTokenModel,
)
async def session_token_view(request: Request):
    """
    Получение токена через сессию
    """
    resources: dict[str, Any] = dict(
        session=request.session, session_config=session_config
    )
    session_token: use_cases.SessionTokenCase = use_cases.SessionTokenCase(**resources)
    return await session_token()


@router.post("/logout", status_code=HTTPStatus.NO_CONTENT)
async def process_logout_view(request: Request):
    """
    Выход с удалением токена из сессии
    """
    resources: dict[str, Any] = dict(
        session=request.session, session_config=session_config
    )
    process_logout: use_cases.ProcessLogoutCase = use_cases.ProcessLogoutCase(
        **resources
    )
    return await process_logout()


@router.patch("/accept", status_code=HTTPStatus.NO_CONTENT)
async def accept_contract_view(
    payload: models.RequestAcceptContractModel = Body(...),
    agent_id: int = Depends(
        dependencies.CurrentUserId(user_type=users_constants.UserType.AGENT)
    ),
):
    """
    Принятие договора
    """
    resources: dict[str, Any] = dict(agent_repo=agents_repos.AgentRepo)
    accept_contract: use_cases.AcceptContractCase = use_cases.AcceptContractCase(
        **resources
    )
    return await accept_contract(agent_id=agent_id, payload=payload)


@router.patch("/change_phone", summary="Смена телефона")
async def initialize_change_phone_view(
    agent_id: int = Depends(
        dependencies.CurrentUserId(user_type=users_constants.UserType.AGENT)
    ),
    payload: models.RequestInitializeChangePhone = Body(...),
):
    """
    Обновление телефона агентом
    """
    get_sms_template_service: notification_services.GetSmsTemplateService = (
        notification_services.GetSmsTemplateService(
            sms_template_repo=notification_repos.SmsTemplateRepo,
        )
    )
    resources: dict[str, Any] = dict(
        site_config=site_config,
        sms_class=messages.SmsService,
        agent_repo=agents_repos.AgentRepo,
        user_type=users_constants.UserType.AGENT,
        token_creator=security.create_email_token,
        get_sms_template_service=get_sms_template_service,
    )
    change_phone: use_cases.InitializeChangePhoneCase = (
        use_cases.InitializeChangePhoneCase(**resources)
    )
    return await change_phone(agent_id=agent_id, payload=payload)


@router.patch("/change_email", summary="Смена почты")
async def initialize_change_email_view(
    agent_id: int = Depends(
        dependencies.CurrentUserId(user_type=users_constants.UserType.AGENT)
    ),
    payload: models.RequestInitializeChangeEmail = Body(...),
):
    """
    Обновление почты агентом
    """
    get_email_template_service: notification_services.GetEmailTemplateService = (
        notification_services.GetEmailTemplateService(
            email_template_repo=notification_repos.EmailTemplateRepo,
        )
    )
    resources: dict[str, Any] = dict(
        site_config=site_config,
        email_class=email.EmailService,
        agent_repo=agents_repos.AgentRepo,
        user_type=users_constants.UserType.AGENT,
        token_creator=security.create_email_token,
        get_email_template_service=get_email_template_service,
    )
    change_email: use_cases.InitializeChangeEmailCase = (
        use_cases.InitializeChangeEmailCase(**resources)
    )
    return await change_email(agent_id=agent_id, payload=payload)


@router.get(
    "/change_phone",
    status_code=HTTPStatus.PERMANENT_REDIRECT,
    summary="Служебный метод для смены телефона",
)
async def change_phone_view(
    token: str = Query(..., alias="q"), change_phone_token: str = Query(..., alias="p")
):
    """
    Служебный эндпоинт для подтверждения изменения телефона
    """
    get_sms_template_service: notification_services.GetSmsTemplateService = (
        notification_services.GetSmsTemplateService(
            sms_template_repo=notification_repos.SmsTemplateRepo,
        )
    )
    resources: dict[str, Any] = dict(
        site_config=site_config,
        sms_class=messages.SmsService,
        agent_repo=agents_repos.AgentRepo,
        user_type=users_constants.UserType.AGENT,
        token_creator=security.create_email_token,
        token_decoder=security.decode_email_token,
        get_sms_template_service=get_sms_template_service,
    )
    change_phone: use_cases.ChangePhoneCase = use_cases.ChangePhoneCase(**resources)
    return RedirectResponse(
        url=await change_phone(token=token, change_phone_token=change_phone_token)
    )


@router.get(
    "/change_email",
    status_code=HTTPStatus.PERMANENT_REDIRECT,
    summary="Служебный метод для смены почты",
)
async def change_email_view(
    token: str = Query(..., alias="q"), change_email_token: str = Query(..., alias="p")
):
    """
    Служебный эндпоинт для подтверждения изменения почты

    """
    get_email_template_service: notification_services.GetEmailTemplateService = (
        notification_services.GetEmailTemplateService(
            email_template_repo=notification_repos.EmailTemplateRepo,
        )
    )
    resources: dict[str, Any] = dict(
        site_config=site_config,
        email_class=email.EmailService,
        agent_repo=agents_repos.AgentRepo,
        user_type=users_constants.UserType.AGENT,
        token_creator=security.create_email_token,
        token_decoder=security.decode_email_token,
        get_email_template_service=get_email_template_service,
    )
    change_email: use_cases.ChangeEmailCase = use_cases.ChangeEmailCase(**resources)
    return RedirectResponse(
        url=await change_email(token=token, change_email_token=change_email_token)
    )


@router.get(
    "/represes",
    status_code=HTTPStatus.OK,
    response_model=models.ResponseRepresesAgentsListModel,
    dependencies=[
        Depends(dependencies.DeletedUserCheck()),
        Depends(dependencies.CurrentUserId(user_type=users_constants.UserType.REPRES)),
    ],
)
async def represes_agents_list_view(
    init_filters: dict[str, Any] = Depends(filters.AgentFilter.filterize),
    agency_id: int = Depends(dependencies.CurrentUserExtra(key="agency_id")),
    pagination: paginations.PagePagination = Depends(
        dependencies.Pagination(page_size=12)
    ),
):
    """
    Список агентов представителя агенства
    """
    resources: dict[str, Any] = dict(
        user_repo=users_repos.UserRepo,
        agent_repo=agents_repos.AgentRepo,
        booking_repo=booking_repos.BookingRepo,
        user_type=users_constants.UserType.AGENT,
        booking_substages=booking_constants.BookingSubstages,
    )
    represes_agents_list: use_cases.RepresesAgentsListCase = (
        use_cases.RepresesAgentsListCase(**resources)
    )
    return await represes_agents_list(
        agency_id=agency_id, pagination=pagination, init_filters=init_filters
    )


@router.get(
    "/represes/specs",
    status_code=HTTPStatus.OK,
    response_model=models.ResponseRepresesAgentsSpecsModel,
    dependencies=[
        Depends(dependencies.DeletedUserCheck()),
        Depends(dependencies.CurrentUserId(user_type=users_constants.UserType.REPRES)),
    ],
)
async def represes_agents_specs_view(
    specs: Callable[..., Coroutine] = Depends(filters.AgentFilter.specs),
    agency_id: int = Depends(dependencies.CurrentUserExtra(key="agency_id")),
):
    """
    Спеки агентов представителей агенства
    """
    resources: dict[str, Any] = dict(
        additional_filters=dict(type=users_constants.UserType.AGENT, is_deleted=False)
    )
    represes_agents_specs: use_cases.RepresesAgentsSpecsCase = (
        use_cases.RepresesAgentsSpecsCase(**resources)
    )
    return await represes_agents_specs(agency_id=agency_id, specs=specs)


@router.get("/represes/booking_specs")
async def represes_useres_specs_statuses_view(
    specs: Callable[..., Coroutine] = Depends(BookingUserFilter.specs),
    agency_id: int = Depends(dependencies.CurrentUserExtra(key="agency_id")),
):
    """Получение всех спеков, связанных со сделками, по агентству"""
    resources: dict[str, Any] = dict(additional_filters={})
    represes_users_specs: use_cases.RepresesAgentsSpecsCase = (
        use_cases.RepresesAgentsSpecsCase(**resources)
    )
    return await represes_users_specs(agency_id=agency_id, specs=specs)


@router.get(
    "/represes/lookup",
    status_code=HTTPStatus.OK,
    response_model=models.ResponseRepresesAgentsLookupModel,
    dependencies=[
        Depends(dependencies.DeletedUserCheck()),
        Depends(dependencies.CurrentUserId(user_type=users_constants.UserType.REPRES)),
    ],
)
async def represes_agents_lookup_view(
    lookup: str = Query(str(), alias="search"),
    init_filters: dict[str, Any] = Depends(filters.AgentFilter.filterize),
    agency_id: int = Depends(dependencies.CurrentUserExtra(key="agency_id")),
):
    """
    Поиск агентов представителя агенства
    """
    resources: dict[str, Any] = dict(
        agent_repo=agents_repos.AgentRepo,
        search_types=users_constants.SearchType,
        user_type=users_constants.UserType.AGENT,
    )
    represes_agents_lookup: use_cases.RepresesAgentsLookupCase = (
        use_cases.RepresesAgentsLookupCase(**resources)
    )
    return await represes_agents_lookup(
        agency_id=agency_id, lookup=lookup, init_filters=init_filters
    )


@router.post(
    "/represes/register",
    status_code=HTTPStatus.CREATED,
    response_model=models.ResponseRepresesAgentsRegisterModel,
    dependencies=[
        Depends(dependencies.DeletedUserCheck()),
        Depends(dependencies.CurrentUserId(user_type=users_constants.UserType.REPRES)),
    ],
    summary="Регистрация агента представителем",
)
async def represes_agents_register_view(
    payload: models.RequestRepresesAgentsRegisterModel = Body(...),
    agency_id: int = Depends(dependencies.CurrentUserExtra(key="agency_id")),
):
    """
    Регистрация агента представителем агентства
    """
    create_contact_service = services.CreateContactService(
        amocrm_class=amocrm.AmoCRM,
        agent_repo=agents_repos.AgentRepo,
        agency_repo=agencies_repos.AgencyRepo,
    )
    ensure_broker_tag_service = services.EnsureBrokerTagService(
        amocrm_class=amocrm.AmoCRM,
        agent_repo=agents_repos.AgentRepo,
    )
    get_sms_template_service: notification_services.GetSmsTemplateService = (
        notification_services.GetSmsTemplateService(
            sms_template_repo=notification_repos.SmsTemplateRepo,
        )
    )
    represes_agents_register = use_cases.RepresesAgentsRegisterCase(
        hasher=security.get_hasher,
        sms_class=messages.SmsService,
        agent_repo=agents_repos.AgentRepo,
        user_type=users_constants.UserType.AGENT,
        create_contact_service=create_contact_service,
        password_generator=utils.generate_simple_password,
        import_clients_task=agents_tasks.import_clients_task,
        ensure_broker_tag_service=ensure_broker_tag_service,
        get_sms_template_service=get_sms_template_service,
    )
    return await represes_agents_register(agency_id=agency_id, payload=payload)


@router.patch(
    "/represes/approval/{agent_id}",
    status_code=HTTPStatus.NO_CONTENT,
    dependencies=[
        Depends(dependencies.DeletedUserCheck()),
        Depends(dependencies.CurrentUserId(user_type=users_constants.UserType.REPRES)),
    ],
)
async def represes_agents_approval_view(
    agent_id: int = Path(...),
    payload: models.RequestRepresesAgentsApprovalModel = Body(...),
    agency_id: int = Depends(dependencies.CurrentUserExtra(key="agency_id")),
):
    """
    Одобрение агента представителем агенства
    """
    create_contact_service = services.CreateContactService(
        amocrm_class=amocrm.AmoCRM,
        agent_repo=agents_repos.AgentRepo,
        agency_repo=agencies_repos.AgencyRepo,
    )
    ensure_broker_tag_service = services.EnsureBrokerTagService(
        amocrm_class=amocrm.AmoCRM,
        agent_repo=agents_repos.AgentRepo,
    )
    get_email_template_service: notification_services.GetEmailTemplateService = (
        notification_services.GetEmailTemplateService(
            email_template_repo=notification_repos.EmailTemplateRepo,
        )
    )
    represes_agents_approval = use_cases.RepresesAgentsApprovalCase(
        site_config=site_config,
        email_class=email.EmailService,
        agent_repo=agents_repos.AgentRepo,
        user_type=users_constants.UserType.AGENT,
        create_contact_service=create_contact_service,
        import_clients_task=agents_tasks.import_clients_task,
        ensure_broker_tag_service=ensure_broker_tag_service,
        get_email_template_service=get_email_template_service,
    )
    return await represes_agents_approval(
        agent_id=agent_id, agency_id=agency_id, payload=payload
    )


@router.get(
    "/represes/{agent_id}",
    status_code=HTTPStatus.OK,
    response_model=models.ResponseRepresesAgentsRetrieveModel,
    dependencies=[
        Depends(dependencies.DeletedUserCheck()),
        Depends(dependencies.CurrentUserId(user_type=users_constants.UserType.REPRES)),
    ],
)
async def represes_agents_retrieve_view(
    agent_id: int = Path(...),
    agency_id: int = Depends(dependencies.CurrentUserExtra(key="agency_id")),
):
    """
    Детальный агент представителя агенства
    """
    resources: dict[str, Any] = dict(
        user_repo=users_repos.UserRepo,
        check_repo=users_repos.CheckRepo,
        agent_repo=agents_repos.AgentRepo,
        user_types=users_constants.UserType,
        booking_repo=booking_repos.BookingRepo,
        booking_substages=booking_constants.BookingSubstages,
    )
    represes_agents_retrieve: use_cases.RepresesAgentsRetrieveCase = (
        use_cases.RepresesAgentsRetrieveCase(**resources)
    )
    return await represes_agents_retrieve(agency_id=agency_id, agent_id=agent_id)


@router.delete(
    "/represes/{agent_id}",
    status_code=HTTPStatus.NO_CONTENT,
    dependencies=[
        Depends(dependencies.DeletedUserCheck()),
        Depends(dependencies.CurrentUserId(user_type=users_constants.UserType.REPRES)),
    ],
)
async def represes_agents_delete_view(
    agent_id: int = Path(...),
    agency_id: int = Depends(dependencies.CurrentUserExtra(key="agency_id")),
):
    """
    Удаление агента представителя агенства
    """
    resources: dict[str, Any] = dict(
        redis=redis.broker,
        redis_config=redis_config,
        user_repo=users_repos.UserRepo,
        check_repo=users_repos.CheckRepo,
        agent_repo=agents_repos.AgentRepo,
        user_types=users_constants.UserType,
        booking_repo=booking_repos.BookingRepo,
    )
    represes_agents_delete: use_cases.RepresesAgentsDeleteCase = (
        use_cases.RepresesAgentsDeleteCase(**resources)
    )
    return await represes_agents_delete(agent_id=agent_id, agency_id=agency_id)


@router.get(
    "/admins",
    status_code=HTTPStatus.OK,
    response_model=models.ResponseAdminsAgentsListModel,
    dependencies=[
        Depends(dependencies.CurrentUserId(user_type=users_constants.UserType.ADMIN))
    ],
)
async def admins_agents_list_view(
    init_filters: dict[str, Any] = Depends(filters.AgentFilter.filterize),
    pagination: paginations.PagePagination = Depends(
        dependencies.Pagination(page_size=12)
    ),
):
    """
    Список агентов администратора
    """
    resources: dict[str, Any] = dict(
        user_repo=users_repos.UserRepo,
        agent_repo=agents_repos.AgentRepo,
        booking_repo=booking_repos.BookingRepo,
        user_type=users_constants.UserType.AGENT,
        booking_substages=booking_constants.BookingSubstages,
    )
    admins_agents_list: use_cases.AdminsAgentsListCase = use_cases.AdminsAgentsListCase(
        **resources
    )
    return await admins_agents_list(pagination=pagination, init_filters=init_filters)


@router.get(
    "/admins/lookup",
    status_code=HTTPStatus.OK,
    response_model=models.ResponseAdminsAgentsLookupModel,
    dependencies=[
        Depends(dependencies.CurrentUserId(user_type=users_constants.UserType.ADMIN))
    ],
)
async def admins_agents_lookup_view(
    lookup: str = Query(str(), alias="search"),
    init_filters: dict[str, Any] = Depends(filters.AgentFilter.filterize),
):
    """
    Поиск агентов администратора
    """
    resources: dict[str, Any] = dict(
        agent_repo=agents_repos.AgentRepo,
        search_types=users_constants.SearchType,
        user_type=users_constants.UserType.AGENT,
    )
    admins_agents_lookup: use_cases.AdminsAgentsLookupCase = (
        use_cases.AdminsAgentsLookupCase(**resources)
    )
    return await admins_agents_lookup(lookup=lookup, init_filters=init_filters)


@router.get(
    "/admins/specs",
    status_code=HTTPStatus.OK,
    response_model=models.ResponseAdminsAgentsSpecsModel,
    dependencies=[
        Depends(dependencies.CurrentUserId(user_type=users_constants.UserType.ADMIN))
    ],
)
async def admins_agents_specs_view(
    specs: Callable[..., Coroutine] = Depends(filters.AgentFilter.specs),
):
    """
    Спеки агентов администратором
    """
    resources: dict[str, Any] = dict(user_type=users_constants.UserType.AGENT)
    admins_agents_specs: use_cases.AdminsAgentsSpecsCase = (
        use_cases.AdminsAgentsSpecsCase(**resources)
    )
    return await admins_agents_specs(specs=specs)


@router.post(
    "/admins/register",
    status_code=HTTPStatus.CREATED,
    response_model=models.ResponseAdminsAgentsRegisterModel,
    dependencies=[
        Depends(dependencies.CurrentUserId(user_type=users_constants.UserType.ADMIN))
    ],
)
async def admins_agents_register_view(
    payload: models.RequestAdminsAgentsRegisterModel = Body(...),
):
    """
    Регистрация агента администратором
    """
    create_contact_service = services.CreateContactService(
        amocrm_class=amocrm.AmoCRM,
        agent_repo=agents_repos.AgentRepo,
        agency_repo=agencies_repos.AgencyRepo,
    )
    ensure_broker_tag_service = services.EnsureBrokerTagService(
        amocrm_class=amocrm.AmoCRM,
        agent_repo=agents_repos.AgentRepo,
    )
    get_sms_template_service: notification_services.GetSmsTemplateService = (
        notification_services.GetSmsTemplateService(
            sms_template_repo=notification_repos.SmsTemplateRepo,
        )
    )
    admins_agents_register = use_cases.AdminsAgentsRegisterCase(
        hasher=security.get_hasher,
        sms_class=messages.SmsService,
        agent_repo=agents_repos.AgentRepo,
        user_type=users_constants.UserType.AGENT,
        create_contact_service=create_contact_service,
        password_generator=utils.generate_simple_password,
        import_clients_task=agents_tasks.import_clients_task,
        ensure_broker_tag_service=ensure_broker_tag_service,
        get_sms_template_service=get_sms_template_service,
    )
    return await admins_agents_register(payload=payload)


@router.patch(
    "/admins/approval/{agent_id}",
    status_code=HTTPStatus.NO_CONTENT,
    dependencies=[
        Depends(dependencies.CurrentUserId(user_type=users_constants.UserType.ADMIN))
    ],
)
async def admins_agents_approval_view(
    agent_id: int = Path(...),
    payload: models.RequestAdminsAgentsApprovalModel = Body(...),
):
    """
    Одобрение агента администратором
    """
    create_contact_service = services.CreateContactService(
        amocrm_class=amocrm.AmoCRM,
        agent_repo=agents_repos.AgentRepo,
        agency_repo=agencies_repos.AgencyRepo,
    )
    ensure_broker_tag_service = services.EnsureBrokerTagService(
        amocrm_class=amocrm.AmoCRM,
        agent_repo=agents_repos.AgentRepo,
    )
    get_email_template_service: notification_services.GetEmailTemplateService = (
        notification_services.GetEmailTemplateService(
            email_template_repo=notification_repos.EmailTemplateRepo,
        )
    )
    admins_agents_approval = use_cases.AdminsAgentsApprovalCase(
        site_config=site_config,
        email_class=email.EmailService,
        agent_repo=agents_repos.AgentRepo,
        user_type=users_constants.UserType.AGENT,
        create_contact_service=create_contact_service,
        import_clients_task=agents_tasks.import_clients_task,
        ensure_broker_tag_service=ensure_broker_tag_service,
        get_email_template_service=get_email_template_service,
    )
    return await admins_agents_approval(agent_id=agent_id, payload=payload)


@router.get(
    "/admins/{agent_id}",
    status_code=HTTPStatus.OK,
    response_model=models.ResponseAdminsAgentsRetrieveModel,
    dependencies=[
        Depends(dependencies.CurrentUserId(user_type=users_constants.UserType.ADMIN))
    ],
)
async def admins_agents_retrieve_view(agent_id: int = Path(...)):
    """
    Детальный агент администратора
    """
    resources: dict[str, Any] = dict(
        user_repo=users_repos.UserRepo,
        check_repo=users_repos.CheckRepo,
        agent_repo=agents_repos.AgentRepo,
        user_types=users_constants.UserType,
        booking_repo=booking_repos.BookingRepo,
        booking_substages=booking_constants.BookingSubstages,
    )
    admins_agents_retrieve: use_cases.AdminsAgentsRetrieveCase = (
        use_cases.AdminsAgentsRetrieveCase(**resources)
    )
    return await admins_agents_retrieve(agent_id=agent_id)


@router.delete(
    "/admins/{agent_id}",
    status_code=HTTPStatus.NO_CONTENT,
    dependencies=[
        Depends(dependencies.CurrentUserId(user_type=users_constants.UserType.ADMIN))
    ],
)
async def admins_agents_delete_view(agent_id: int = Path(...)):
    """
    Удаление агента администратором
    """
    resources: dict[str, Any] = dict(
        redis=redis.broker,
        redis_config=redis_config,
        user_repo=users_repos.UserRepo,
        check_repo=users_repos.CheckRepo,
        agent_repo=agents_repos.AgentRepo,
        user_types=users_constants.UserType,
        booking_repo=booking_repos.BookingRepo,
    )
    admins_agents_delete: use_cases.AdminsAgentsDeleteCase = (
        use_cases.AdminsAgentsDeleteCase(**resources)
    )
    return await admins_agents_delete(agent_id=agent_id)


@router.patch(
    "/admins/{agent_id}",
    status_code=HTTPStatus.NO_CONTENT,
    dependencies=[
        Depends(dependencies.CurrentUserId(user_type=users_constants.UserType.ADMIN))
    ],
)
async def admins_agents_update_view(
    agent_id: int = Path(...),
    payload: models.RequestAdminsAgentsUpdateModel = Body(...),
):
    """
    Обновление агента администратором
    """
    get_email_template_service: notification_services.GetEmailTemplateService = (
        notification_services.GetEmailTemplateService(
            email_template_repo=notification_repos.EmailTemplateRepo,
        )
    )
    get_sms_template_service: notification_services.GetSmsTemplateService = (
        notification_services.GetSmsTemplateService(
            sms_template_repo=notification_repos.SmsTemplateRepo,
        )
    )
    resources: dict[str, Any] = dict(
        site_config=site_config,
        sms_class=messages.SmsService,
        email_class=email.EmailService,
        agent_repo=agents_repos.AgentRepo,
        user_type=users_constants.UserType.AGENT,
        token_creator=security.create_email_token,
        get_email_template_service=get_email_template_service,
        get_sms_template_service=get_sms_template_service,
    )
    admins_agents_update: use_cases.AdminsAgentsUpdateCase = (
        use_cases.AdminsAgentsUpdateCase(**resources)
    )
    return await admins_agents_update(agent_id=agent_id, payload=payload)


@router.get(
    "/questionnaire/{slug}",
    status_code=HTTPStatus.OK,
    response_model=list[models.QuestionsListResponse],
    dependencies=[
        Depends(dependencies.CurrentUserId(user_type=users_constants.UserType.AGENT))
    ],
)
async def agents_questionnaire_question_list(
    slug: str = Path(..., description="slug функционального блока"),
    booking_id: int = Query(..., description="ID сделки"),
):
    """
    Получение вопроса опросника
    """
    resources: dict[str, Any] = dict(
        question_repo=questionnaire_repos.QuestionRepo,
        answer_repo=questionnaire_repos.AnswerRepo,
        users_answer_repo=questionnaire_repos.UserAnswerRepo,
        booking_repo=booking_repos.BookingRepo,
    )
    questions_list: use_cases.QuestionsListResponseCase = (
        use_cases.QuestionsListResponseCase(**resources)
    )
    return await questions_list(slug=slug, booking_id=booking_id)


@router.patch(
    "/questionnaire/{question_id}",
    status_code=HTTPStatus.NO_CONTENT,
    dependencies=[
        Depends(dependencies.CurrentUserId(user_type=users_constants.UserType.AGENT))
    ],
)
async def agents_questionnaire_save_answer(
    payload: models.CurrentAnswerRequest,
    question_id: int = Path(..., description="ID вопроса"),
):
    """
    Сохранение ответа
    """
    resources: dict[str, Any] = dict(
        question_repo=questionnaire_repos.QuestionRepo,
        booking_repo=booking_repos.BookingRepo,
        users_answer_repo=questionnaire_repos.UserAnswerRepo,
    )
    save_answer: use_cases.QuestionareSaveAnswerCase = (
        use_cases.QuestionareSaveAnswerCase(**resources)
    )
    await save_answer(question_id=question_id, payload=payload)
    return Response(status_code=HTTPStatus.NO_CONTENT)


@router.put(
    "/questionnaire/{slug}/finish",
    status_code=HTTPStatus.OK,
    response_model=models.FinishQuestionResultResponse,
    dependencies=[
        Depends(dependencies.CurrentUserId(user_type=users_constants.UserType.AGENT))
    ],
)
async def agents_questionnaire_finish(
    payload: models.FinishQuestionRequest,
    slug: str = Path(..., description="slug функционального блока"),
):
    """
    Конец опросника
    """
    resources: dict[str, Any] = dict(
        question_repo=questionnaire_repos.QuestionRepo,
        booking_repo=booking_repos.BookingRepo,
    )
    finish_answer: use_cases.QuestionareFinishCase = use_cases.QuestionareFinishCase(
        **resources
    )
    return await finish_answer(slug=slug, payload=payload)


@router.put(
    "/bookings/{booking_id}/upload-documents/{document_id}",
    status_code=HTTPStatus.OK,
    response_model=models.UploadFile,
    dependencies=[
        Depends(dependencies.CurrentUserId(user_type=users_constants.UserType.AGENT))
    ],
)
async def agents_upload_documents(
    booking_id: int = Path(..., description="ID сделки"),
    document_id: int = Path(..., description="ID документа"),
    file_uuid: Optional[UUID] = Query(None, description="UUID файла"),
    file: UploadFile = File(
        ..., description="Загружаемый документ", max_upload_size=5_000_000
    ),
):
    """
    Загрузка документов в амо
    """
    resources: dict[str, Any] = dict(
        booking_repo=booking_repos.BookingRepo,
        document_repo=questionnaire_repos.QuestionnaireDocumentRepo,
        upload_document_repo=questionnaire_repos.QuestionnaireUploadDocumentRepo,
        amocrm_uploader_class=amocrm.AmoCRMFileUploader,
    )
    upload_document: use_cases.QuestionareUploadDocumentCase = (
        use_cases.QuestionareUploadDocumentCase(**resources)
    )
    return await upload_document(
        document_id=document_id, booking_id=booking_id, file_uuid=file_uuid, file=file
    )


@router.get(
    "/questionnaire/{slug}/groups_of_documents/{booking_id}",
    status_code=HTTPStatus.OK,
    response_model=list[models.DocumentBlockResponse],
    dependencies=[
        Depends(dependencies.CurrentUserId(user_type=users_constants.UserType.AGENT))
    ],
)
async def agents_bookings_upload_documents(
    booking_id: int = Path(..., description="ID сделки"),
    slug: str = Path(..., description="slug функционального блока"),
):
    """
    Получение списка загруженных документов
    """
    resources: dict[str, Any] = dict(
        booking_repo=booking_repos.BookingRepo,
        document_block_repo=questionnaire_repos.QuestionnaireDocumentBlockRepo,
        document_repo=questionnaire_repos.QuestionnaireDocumentRepo,
        upload_document_repo=questionnaire_repos.QuestionnaireUploadDocumentRepo,
        functional_block_repo=questionnaire_repos.FunctionalBlockRepo,
    )
    upload_documents_list: use_cases.UploadDocumentsBlocksListCase = (
        use_cases.UploadDocumentsBlocksListCase(**resources)
    )
    return await upload_documents_list(slug=slug, booking_id=booking_id)


@router.post(
    "/questionnaire/{booking_id}/send",
    status_code=HTTPStatus.OK,
    dependencies=[
        Depends(dependencies.CurrentUserId(user_type=users_constants.UserType.AGENT))
    ],
)
async def agents_bookings_send_upload_documents(
    booking_id: int = Path(..., description="ID сделки"),
):
    """
    Отправка url загруженных документов в АМО
    """
    update_task_instance_status_service = UpdateTaskInstanceStatusServiceFactory.create()
    resources: dict[str, Any] = dict(
        booking_repo=booking_repos.BookingRepo,
        upload_document_repo=questionnaire_repos.QuestionnaireUploadDocumentRepo,
        amocrm_class=amocrm.AmoCRM,
        update_task_instance_status_service=update_task_instance_status_service,
    )
    send_upload_documents: use_cases.SendUploadDocumentsCase = (
        use_cases.SendUploadDocumentsCase(**resources)
    )
    await send_upload_documents(booking_id=booking_id)
    return Response(status_code=HTTPStatus.ACCEPTED)


@router.delete(
    "/questionnaire/upload-documents",
    status_code=HTTPStatus.NO_CONTENT,
)
async def agents_delete_upload_documents(
    upload_documents_ids: list[UUID],
    agent_id: int = Depends(
        dependencies.CurrentUserId(user_type=users_constants.UserType.AGENT)
    ),
):
    """
    Удаление загруженных документов по UUID
    """
    resources: dict[str, Any] = dict(
        upload_document_repo=questionnaire_repos.QuestionnaireUploadDocumentRepo,
    )
    delete_upload_documents: use_cases.DeleteUploadDocumentsCase = (
        use_cases.DeleteUploadDocumentsCase(**resources)
    )
    await delete_upload_documents(
        upload_documents_ids=upload_documents_ids, agent_id=agent_id
    )
    return Response(status_code=HTTPStatus.NO_CONTENT)


@router.post(
    "/join_agency",
    status_code=HTTPStatus.OK,
    response_model=models.ResponseSignupInAgencyModel,
)
async def process_signup_in_agency(
    payload: models.RequestSignupInAgencyModel = Body(...),
    agent_id: int = Depends(
        dependencies.CurrentUserId(user_type=users_constants.UserType.AGENT)
    ),
):
    """
    Восстановление агента в новом агентстве.
    """
    create_contact_service = services.CreateContactService(
        amocrm_class=amocrm.AmoCRM,
        agent_repo=agents_repos.AgentRepo,
        agency_repo=agencies_repos.AgencyRepo,
    )
    ensure_broker_tag_service = services.EnsureBrokerTagService(
        amocrm_class=amocrm.AmoCRM,
        agent_repo=agents_repos.AgentRepo,
    )
    get_email_template_service: notification_services.GetEmailTemplateService = (
        notification_services.GetEmailTemplateService(
            email_template_repo=notification_repos.EmailTemplateRepo,
        )
    )
    resources: dict[str, Any] = dict(
        agent_repo=agents_repos.AgentRepo,
        agency_repo=agencies_repos.AgencyRepo,
        email_class=email.EmailService,
        create_contact_service=create_contact_service,
        ensure_broker_tag_service=ensure_broker_tag_service,
        bind_contact_company_task=bind_contact_to_company,
        site_config=site_config,
        get_email_template_service=get_email_template_service,
    )
    process_signup_in_agency: use_cases.ProcessSignupInAgency = (
        use_cases.ProcessSignupInAgency(**resources)
    )
    return await process_signup_in_agency(agent_id=agent_id, payload=payload)


@router.post(
    "/get_current_account_loyalty_points",
    status_code=HTTPStatus.OK,
)
async def get_current_account_loyalty_points(
    payload: models.LoyaltyStatusRequestModel = Body(...),
    agent_amocrm_id: int = Depends(dependencies.CurrentOptionalUserIdWithoutRole()),
):
    """
    Импорт данных агента по программе лояльности из МС Лояльности.
    """
    resources: dict[str, Any] = dict(
        agent_repo=agents_repos.AgentRepo,
        booking_repo=booking_repos.BookingRepo,
    )
    get_current_account_loyalty_points_case: use_cases.GetCurrentAccountLoyaltyPointsCase = \
        use_cases.GetCurrentAccountLoyaltyPointsCase(
            **resources
        )
    return await get_current_account_loyalty_points_case(
        agent_amocrm_id=agent_amocrm_id, payload=payload
    )
