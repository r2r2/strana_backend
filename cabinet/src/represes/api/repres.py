from http import HTTPStatus
from typing import Any, Optional


from common import dependencies, email, files, security, messages
from common.amocrm import AmoCRM
from common.amocrm.tasks import bind_contact_to_company
from config import auth_config, session_config, site_config
from fastapi import (APIRouter, Body, Depends, File, Form, Query, Request,
                     UploadFile)
from fastapi.responses import RedirectResponse
from pydantic import Json
from src.admins import repos as admins_repos
from src.agencies import repos as agencies_repos
from src.agencies.services import CreateOrganizationService
from src.agents import repos as agent_repos
from src.represes.services import CreateContactService
from src.represes import models
from src.represes import use_cases
from src.users import constants as users_constants
from src.users import use_cases as users_cases
from src.users import services as user_services
from src.notifications import services as notification_services
from src.notifications import repos as notification_repos
from src.agencies import use_cases as agencies_use_cases
from src.agencies import tasks as agency_tasks
from src.agents import repos as agents_repos
from src.users import repos as users_repos
from src.booking import repos as booking_repos
from src.represes import repos as represes_repos
from src.agencies import models as agencies_models

router = APIRouter(prefix="/represes", tags=["Representatives"])


@router.post("/register",
             status_code=HTTPStatus.CREATED,
             response_model=models.ResponseProcessRegisterModel,
             summary="Регистрация агентства")
async def process_register_view(
    payload: Json[models.RequestProcessRegisterModel] = Form(...),
    inn_files: Optional[list[UploadFile]] = File(None),
    ogrn_files: Optional[list[UploadFile]] = File(None),
    ogrnip_files: Optional[list[UploadFile]] = File(None),
    charter_files: Optional[list[UploadFile]] = File(None),
    company_files: Optional[list[UploadFile]] = File(None),
    passport_files: Optional[list[UploadFile]] = File(None),
    procuratory_files: Optional[list[UploadFile]] = File(None),
):
    """
    Регистрация
    """
    payload: models.RequestProcessRegisterModel
    resources: dict[str, Any] = dict(
        amocrm_class=AmoCRM,
        repres_repo=represes_repos.RepresRepo,
        agency_repo=agencies_repos.AgencyRepo,
    )
    create_contact_service: CreateContactService = (
        CreateContactService(**resources)
    )
    resources: dict[str, Any] = dict(
        amocrm_class=AmoCRM, agency_repo=agencies_repos.AgencyRepo
    )
    create_organization_service: CreateOrganizationService = (
        CreateOrganizationService(**resources)
    )
    get_email_template_service: notification_services.GetEmailTemplateService = \
        notification_services.GetEmailTemplateService(
            email_template_repo=notification_repos.EmailTemplateRepo,
        )
    check_user_unique_service: user_services.UserCheckUniqueService = user_services.UserCheckUniqueService(
        user_repo=users_repos.UserRepo,
    )
    process_register: use_cases.ProcessRegisterCase = use_cases.ProcessRegisterCase(
        admin_repo=admins_repos.AdminRepo,
        agency_repo=agencies_repos.AgencyRepo,
        email_class=email.EmailService,
        file_processor=files.FileProcessor,
        hasher=security.get_hasher,
        repres_repo=represes_repos.RepresRepo,
        site_config=site_config,
        token_creator=security.create_email_token,
        agent_repo=agent_repos.AgentRepo,
        create_contact_service=create_contact_service,
        create_organization_service=create_organization_service,
        bind_contact_to_company=bind_contact_to_company,
        get_email_template_service=get_email_template_service,
        check_user_unique_service=check_user_unique_service,
    )
    return await process_register(
        payload=payload,
        inn_files=inn_files,
        ogrn_files=ogrn_files,
        ogrnip_files=ogrnip_files,
        charter_files=charter_files,
        company_files=company_files,
        passport_files=passport_files,
        procuratory_files=procuratory_files,
    )


@router.get("/confirm_email",
            status_code=HTTPStatus.PERMANENT_REDIRECT,
            summary="Подтверждение почты")
async def confirm_email_view(
    token: str = Query(..., alias="q"), email_token: str = Query(..., alias="p")
):
    """
    Служебный эндпоинт для подтверждения почты
    """
    resources: dict[str, Any] = dict(
        site_config=site_config,
        repres_repo=represes_repos.RepresRepo,
        user_type=users_constants.UserType.REPRES,
        token_decoder=security.decode_email_token,
    )
    confirm_email: use_cases.ConfirmEmailCase = use_cases.ConfirmEmailCase(**resources)
    return RedirectResponse(url=await confirm_email(token=token, email_token=email_token))


@router.post(
    "/resend_email_verification",
    status_code=HTTPStatus.OK,
    summary="Отправка письма на подтверждение почты"
)
async def resend_confirm_letter_view(
    repres_id: Optional[int] = Depends(
        dependencies.CurrentUserId(user_type=users_constants.UserType.REPRES)
    )
):
    """Отправляет письмо подтверждения на почту агенту."""
    # возможно, необходимо добавить cooldown-таймер
    get_email_template_service: notification_services.GetEmailTemplateService = \
        notification_services.GetEmailTemplateService(
            email_template_repo=notification_repos.EmailTemplateRepo,
        )
    resources: dict[str, Any] = dict(
        site_config=site_config,
        email_class=email.EmailService,
        repres_repo=represes_repos.RepresRepo,
        token_creator=security.create_email_token,
        get_email_template_service=get_email_template_service,
    )
    resend_letter: use_cases.RepresResendLetterCase = use_cases.RepresResendLetterCase(
        **resources
    )
    return await resend_letter(repres_id)


@router.get("/reset_password",
            status_code=HTTPStatus.PERMANENT_REDIRECT,
            summary="Сброс пароля")
async def reset_password_view(
    request: Request, token: str = Query(..., alias="q"), discard_token: str = Query(..., alias="p")
):
    """
    Служебный эндпоинт для сброса пароля
    """
    resources: dict[str, Any] = dict(
        site_config=site_config,
        auth_config=auth_config,
        session=request.session,
        session_config=session_config,
        repres_repo=represes_repos.RepresRepo,
        user_type=users_constants.UserType.REPRES,
        token_decoder=security.decode_email_token,
    )
    reset_password: use_cases.ResetPasswordCase = use_cases.ResetPasswordCase(**resources)
    return RedirectResponse(url=await reset_password(token=token, discard_token=discard_token))


@router.get("/reset_available",
            status_code=HTTPStatus.OK,
            response_model=models.ResponseResetAvailableModel,
            summary="Доступность сброса пароля")
async def reset_available_view(request: Request):
    """
    Доступность сброса пароля
    """
    resources: dict[str, Any] = dict(
        session=request.session,
        session_config=session_config,
        repres_repo=represes_repos.RepresRepo,
        user_type=users_constants.UserType.REPRES,
    )
    reset_available: use_cases.ResetAvailableCase = use_cases.ResetAvailableCase(**resources)
    return await reset_available()


@router.patch("/change_password",
              status_code=HTTPStatus.OK,
              summary="Смена пароля")
async def change_password_view(
    request: Request,
    payload: models.RequestChangePasswordModel = Body(...),
    repres_id: Optional[int] = Depends(
        dependencies.CurrentUserId(user_type=users_constants.UserType.REPRES)
    ),
):
    """
    Смена пароля
    """
    resources: dict[str, Any] = dict(
        session=request.session,
        hasher=security.get_hasher,
        session_config=session_config,
        user_repo=represes_repos.RepresRepo,
        user_type=users_constants.UserType.REPRES,
    )
    change_password: users_cases.ChangePasswordCase = users_cases.ChangePasswordCase(**resources)
    return await change_password(user_id=repres_id, payload=payload)


@router.patch("/change_email", summary="Смена почты")
async def initialize_change_email_view(
    repres_id: int = Depends(dependencies.CurrentUserId(user_type=users_constants.UserType.REPRES)),
    payload: models.RequestInitializeChangeEmail = Body(...)
):
    """
    Обновление почты представителем агентства
    """
    get_email_template_service: notification_services.GetEmailTemplateService = \
        notification_services.GetEmailTemplateService(
            email_template_repo=notification_repos.EmailTemplateRepo,
        )
    resources: dict[str, Any] = dict(
        site_config=site_config,
        email_class=email.EmailService,
        repres_repo=represes_repos.RepresRepo,
        user_type=users_constants.UserType.REPRES,
        token_creator=security.create_email_token,
        get_email_template_service=get_email_template_service,
    )
    change_email: use_cases.InitializeChangeEmailCase = use_cases.InitializeChangeEmailCase(**resources)
    return await change_email(repres_id=repres_id, payload=payload)


@router.patch("/change_phone", summary="Смена телефона")
async def initialize_change_phone_view(
    repres_id: int = Depends(dependencies.CurrentUserId(user_type=users_constants.UserType.REPRES)),
    payload: models.RequestInitializeChangePhone = Body(...)
):
    """Обновление телефона представителем агентства"""
    get_sms_template_service: notification_services.GetSmsTemplateService = \
        notification_services.GetSmsTemplateService(
            sms_template_repo=notification_repos.SmsTemplateRepo,
        )
    resources: dict[str, Any] = dict(
        site_config=site_config,
        sms_class=messages.SmsService,
        repres_repo=represes_repos.RepresRepo,
        user_type=users_constants.UserType.REPRES,
        token_creator=security.create_email_token,
        get_sms_template_service=get_sms_template_service,
    )
    change_phone: use_cases.InitializeChangePhoneCase = use_cases.InitializeChangePhoneCase(**resources)
    return await change_phone(repres_id=repres_id, payload=payload)


@router.post("/set_password",
             status_code=HTTPStatus.OK,
             response_model=models.ResponseSetPasswordModel,
             summary="Установка пароля для созданных представителем")
async def set_password_view(request: Request, payload: models.RequestSetPasswordModel = Body(...)):
    """
    Установка пароля для созданных представителем
    """
    get_email_template_service: notification_services.GetEmailTemplateService = \
        notification_services.GetEmailTemplateService(
            email_template_repo=notification_repos.EmailTemplateRepo,
        )
    resources: dict[str, Any] = dict(
        session=request.session,
        site_config=site_config,
        hasher=security.get_hasher,
        session_config=session_config,
        email_class=email.EmailService,
        repres_repo=represes_repos.RepresRepo,
        user_type=users_constants.UserType.REPRES,
        token_creator=security.create_email_token,
        get_email_template_service=get_email_template_service,
    )
    set_password: use_cases.SetPasswordCase = use_cases.SetPasswordCase(**resources)
    return await set_password(payload=payload)


@router.post("/login",
             status_code=HTTPStatus.OK,
             response_model=models.ResponseProcessLoginModel,
             summary="Вход")
async def process_login_view(
    request: Request, payload: models.RequestProcessLoginModel = Body(...)
):
    """
    Вход
    """
    handler: users_cases.UserAgencyHandler = users_cases.UserAgencyHandler()
    handler.set_next(None)

    resources: dict[str, Any] = dict(
        auth_config=auth_config,
        session=request.session,
        hasher=security.get_hasher,
        login_handler=handler,
        session_config=session_config,
        user_repo=represes_repos.RepresRepo,
        user_type=users_constants.UserType.REPRES,
        token_creator=security.create_access_token,
    )
    process_login: use_cases.ProcessLoginCase = use_cases.ProcessLoginCase(**resources)
    return await process_login(payload=payload)


@router.get("/me",
            status_code=HTTPStatus.OK,
            response_model=models.ResponseUserInfoBaseModel,
            summary="Получение текущего представителя")
async def get_me_view(
    repres_id: int = Depends(dependencies.CurrentUserId(user_type=users_constants.UserType.REPRES)),
):
    """
    Получение текущего представителя
    """
    resources: dict[str, Any] = dict(repres_repo=represes_repos.RepresRepo)
    get_me: use_cases.GetMeCase = use_cases.GetMeCase(**resources)
    return await get_me(repres_id=repres_id)


@router.get(
    "/profile",
    status_code=HTTPStatus.OK,
    response_model=models.ResponseProfileModel,
    summary="Профиль представителя"
)
async def get_profile_view(
    repres_id: int = Depends(dependencies.CurrentUserId(user_type=users_constants.UserType.REPRES)),
):
    """
    Получение профиля текущего представителя
    """
    resources: dict[str, Any] = dict(repres_repo=represes_repos.RepresRepo)
    get_me: use_cases.GetMeCase = use_cases.GetMeCase(**resources)
    return await get_me(repres_id=repres_id)


@router.patch(
    "/profile",
    status_code=HTTPStatus.OK,
    response_model=models.ResponseProfileModel,
    summary="Обновление профиля представителя")
async def update_me_view(
    repres_id: int = Depends(dependencies.CurrentUserId(user_type=users_constants.UserType.REPRES)),
    payload: models.UpdateProfileModel = Body(...)
):
    """
    API метод для обновления данных представителя
    """
    resources = dict(
        repres_repo=represes_repos.RepresRepo,
        user_type=users_constants.UserType.REPRES,
        amocrm_class=AmoCRM
    )
    update_me: use_cases.UpdateProfileCase = use_cases.UpdateProfileCase(**resources)
    return await update_me(repres_id=repres_id, payload=payload)


@router.get("/session_token",
            status_code=HTTPStatus.OK,
            response_model=models.ResponseSessionTokenModel,
            summary="Получение токена через сессию")
async def session_token_view(request: Request):
    """
    Получение токена через сессию
    """
    resources: dict[str, Any] = dict(session=request.session, session_config=session_config)
    session_token: use_cases.SessionTokenCase = use_cases.SessionTokenCase(**resources)
    return await session_token()


@router.post("/logout",
             status_code=HTTPStatus.NO_CONTENT,
             summary="Выход с удалением токена из сессии")
async def process_logout_view(request: Request):
    """
    Выход с удалением токена из сессии
    """
    resources: dict[str, Any] = dict(session=request.session, session_config=session_config)
    process_logout: use_cases.ProcessLogoutCase = use_cases.ProcessLogoutCase(**resources)
    return await process_logout()


@router.patch("/accept",
              status_code=HTTPStatus.NO_CONTENT,
              summary="Принятие договора")
async def accept_contract_view(
    payload: models.RequestAcceptContractModel = Body(...),
    repres_id: int = Depends(dependencies.CurrentUserId(user_type=users_constants.UserType.REPRES)),
):
    """
    Принятие договора
    """
    resources: dict[str, Any] = dict(repres_repo=represes_repos.RepresRepo)
    accept_contract: use_cases.AcceptContractCase = use_cases.AcceptContractCase(**resources)
    return await accept_contract(repres_id=repres_id, payload=payload)


@router.patch(
    "/fire_agent",
    status_code=HTTPStatus.OK,
    response_model=agencies_models.ResponseFireAgentBookingsListModel,
    dependencies=[Depends(dependencies.DeletedUserCheck())],
)
async def repres_fire_agent(
    agent_id: int = Query(...),
    repres_id: int = Depends(dependencies.CurrentUserId(user_type=users_constants.UserType.REPRES)),
):
    """
    Увольнение агента представителем агентства.
    """
    get_email_template_service: notification_services.GetEmailTemplateService = \
        notification_services.GetEmailTemplateService(
            email_template_repo=notification_repos.EmailTemplateRepo,
        )
    resources: dict[str, Any] = dict(
        user_repo=users_repos.UserRepo,
        agent_repo=agents_repos.AgentRepo,
        repres_repo=represes_repos.RepresRepo,
        booking_repo=booking_repos.BookingRepo,
        fire_agent_task=agency_tasks.fire_agent_task,
        email_class=email.EmailService,
        get_email_template_service=get_email_template_service,
    )
    repres_fire_agent_case: agencies_use_cases.FireAgentCase = (
        agencies_use_cases.FireAgentCase(**resources)
    )
    return await repres_fire_agent_case(
        agent_id=agent_id,
        repres_id=repres_id,
        role=users_constants.UserType.REPRES,
    )
