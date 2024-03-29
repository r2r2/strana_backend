from http import HTTPStatus
from typing import Any, Optional

from fastapi import APIRouter, Body, Request, Query, Depends, status
from fastapi.responses import RedirectResponse

from common import messages, security, utils, email, dependencies
from config import auth_config, session_config, site_config
from src.admins import repos as admins_repos
from src.admins import use_cases, models
from src.users import constants as users_constants
from src.users import use_cases as users_cases
from src.notifications import services as notification_services
from src.notifications import repos as notification_repos
from src.agencies import use_cases as agencies_use_cases
from src.agencies import tasks as agency_tasks
from src.agents import repos as agents_repos
from src.users import repos as users_repos
from src.booking import repos as booking_repos
from src.represes import repos as represes_repos
from src.agencies import models as agencies_models


router = APIRouter(prefix="/admins", tags=["Admins"])


@router.post(
    "/register", status_code=status.HTTP_201_CREATED, response_model=models.ResponseProcessRegisterModel
)
async def process_register_view(payload: models.RequestProcessAdminRegisterModel = Body(...)):
    """
    Регистрация администратора
    """
    resources: dict[str, Any] = dict(
        hasher=security.get_hasher,
        sms_class=messages.SmsService,
        admin_repo=admins_repos.AdminRepo,
        user_type=users_constants.UserType.ADMIN,
        password_generator=utils.generate_simple_password,
    )
    process_register: use_cases.ProcessRegisterCase = use_cases.ProcessRegisterCase(**resources)
    return await process_register(payload=payload)


@router.get("/confirm_email", status_code=HTTPStatus.PERMANENT_REDIRECT)
async def confirm_email_view(
    token: str = Query(..., alias="q"), email_token: str = Query(..., alias="p")
):
    """
    Подтверждение почты
    """
    resources: dict[str, Any] = dict(
        site_config=site_config,
        admin_repo=admins_repos.AdminRepo,
        user_type=users_constants.UserType.ADMIN,
        token_decoder=security.decode_email_token,
    )
    confirm_email: use_cases.ConfirmEmailCase = use_cases.ConfirmEmailCase(**resources)
    return RedirectResponse(url=await confirm_email(token=token, email_token=email_token))


@router.get("/reset_password", status_code=HTTPStatus.PERMANENT_REDIRECT)
async def reset_password_view(
    request: Request, token: str = Query(..., alias="q"), discard_token: str = Query(..., alias="p")
):
    """
    Сброс пароля
    """
    resources: dict[str, Any] = dict(
        site_config=site_config,
        auth_config=auth_config,
        session=request.session,
        session_config=session_config,
        admin_repo=admins_repos.AdminRepo,
        user_type=users_constants.UserType.ADMIN,
        token_decoder=security.decode_email_token,
    )
    reset_password: use_cases.ResetPasswordCase = use_cases.ResetPasswordCase(**resources)
    return RedirectResponse(url=await reset_password(token=token, discard_token=discard_token))


@router.get(
    "/reset_available", status_code=HTTPStatus.OK, response_model=models.ResponseResetAvailableModel
)
async def reset_available_view(request: Request):
    """
    Доступность сброса пароля
    """
    resources: dict[str, Any] = dict(
        session=request.session,
        session_config=session_config,
        admin_repo=admins_repos.AdminRepo,
        user_type=users_constants.UserType.ADMIN,
    )
    reset_available: use_cases.ResetAvailableCase = use_cases.ResetAvailableCase(**resources)
    return await reset_available()


@router.patch("/change_password", status_code=HTTPStatus.OK)
async def change_password_view(
    request: Request,
    payload: models.RequestChangePasswordModel = Body(...),
    admin_id: Optional[int] = Depends(
        dependencies.CurrentUserId(user_type=users_constants.UserType.ADMIN)
    ),
):
    """
    Смена пароля
    """
    resources: dict[str, Any] = dict(
        session=request.session,
        hasher=security.get_hasher,
        session_config=session_config,
        user_repo=admins_repos.AdminRepo,
        user_type=users_constants.UserType.ADMIN,
    )
    change_password: users_cases.ChangePasswordCase = users_cases.ChangePasswordCase(**resources)
    return await change_password(user_id=admin_id, payload=payload)


@router.post(
    "/set_password", status_code=HTTPStatus.OK, response_model=models.ResponseSetPasswordModel
)
async def set_password_view(request: Request, payload: models.RequestSetPasswordModel = Body(...)):
    """
    Установка пароля
    """
    resources: dict[str, Any] = dict(
        session=request.session,
        site_config=site_config,
        hasher=security.get_hasher,
        session_config=session_config,
        email_class=email.EmailService,
        admin_repo=admins_repos.AdminRepo,
        user_type=users_constants.UserType.ADMIN,
    )
    set_password: use_cases.SetPasswordCase = use_cases.SetPasswordCase(**resources)
    return await set_password(payload=payload)


@router.post("/login", status_code=HTTPStatus.OK, response_model=models.ResponseProcessLoginModel)
async def process_login_view(
    request: Request, payload: models.RequestProcessLoginModel = Body(...)
):
    """
    Вход администратора
    """
    resources: dict[str, Any] = dict(
        auth_config=auth_config,
        session=request.session,
        hasher=security.get_hasher,
        session_config=session_config,
        user_repo=admins_repos.AdminRepo,
        token_creator=security.create_access_token,
    )
    process_login: use_cases.ProcessLoginCase = use_cases.ProcessLoginCase(**resources)
    return await process_login(payload=payload)


@router.get("/me", status_code=HTTPStatus.OK, response_model=models.ResponseGetMeModel)
async def get_me_view(
    admin_id: int = Depends(dependencies.CurrentUserId(user_type=users_constants.UserType.ADMIN)),
):
    """
    Получение текущего администратора
    """
    resources: dict[str, Any] = dict(admin_repo=admins_repos.AdminRepo)
    get_me: use_cases.GetMeCase = use_cases.GetMeCase(**resources)
    return await get_me(admin_id=admin_id)


@router.post("/logout", status_code=HTTPStatus.NO_CONTENT)
async def process_logout_view(request: Request):
    """
    Выход с удалением токена из сессии
    """
    resources: dict[str, Any] = dict(session=request.session, session_config=session_config)
    process_logout: use_cases.ProcessLogoutCase = use_cases.ProcessLogoutCase(**resources)
    return await process_logout()


@router.patch(
    "/fire_agent",
    status_code=HTTPStatus.OK,
    response_model=agencies_models.ResponseFireAgentBookingsListModel,
    dependencies=[
        Depends(dependencies.DeletedUserCheck()),
        Depends(dependencies.CurrentUserId(user_type=users_constants.UserType.ADMIN)),
    ],
)
async def admin_fire_agent(agent_id: int = Query(...)):
    """
    Увольнение агента админом.
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
    admin_fire_agent_case: agencies_use_cases.FireAgentCase = (
        agencies_use_cases.FireAgentCase(**resources)
    )
    return await admin_fire_agent_case(
        agent_id=agent_id,
        role=users_constants.UserType.ADMIN,
    )
