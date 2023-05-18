from http import HTTPStatus
from typing import Any, Optional

from fastapi import APIRouter, Body, Request, Query, Depends
from fastapi.responses import RedirectResponse

from common import messages, security, utils, email, dependencies
from config import auth_config, session_config, site_config
from src.admins import repos as admins_repos
from src.admins import use_cases, models
from src.users import constants as users_constants
from src.users import use_cases as users_cases


router = APIRouter(prefix="/admins", tags=["Admins"])


@router.post(
    "/register", status_code=HTTPStatus.CREATED, response_model=models.ResponseProcessRegisterModel
)
async def process_register_view(payload: models.RequestProcessRegisterModel = Body(...)):
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


@router.post("/email_reset", status_code=HTTPStatus.NO_CONTENT)
async def email_reset_view(payload: models.RequestEmailResetModel = Body(...)):
    """
    Ссылка для сброса пароля
    """
    resources: dict[str, Any] = dict(
        site_config=site_config,
        email_class=email.EmailService,
        admin_repo=admins_repos.AdminRepo,
        user_type=users_constants.UserType.ADMIN,
        token_creator=security.create_email_token,
    )
    email_reset: use_cases.EmailResetCase = use_cases.EmailResetCase(**resources)
    return await email_reset(payload=payload)


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
        user_type=users_constants.UserType.ADMIN,
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


@router.post("/logout", status_code=HTTPStatus.NO_CONTENT)
async def process_logout_view(request: Request):
    """
    Выход с удалением токена из сессии
    """
    resources: dict[str, Any] = dict(session=request.session, session_config=session_config)
    process_logout: use_cases.ProcessLogoutCase = use_cases.ProcessLogoutCase(**resources)
    return await process_logout()
