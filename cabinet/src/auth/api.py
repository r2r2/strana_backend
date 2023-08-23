from http import HTTPStatus
from typing import Any

from common import security
from config import auth_config, session_config, site_config
from fastapi import APIRouter, Body, Request, Query, Header
from src.admins import repos as admins_repos
from src.users import constants as users_constants
from src.users import models, use_cases
from src.users import repos as users_repos

router = APIRouter(prefix="/auth", tags=["Auth"])


@router.post("/email", status_code=HTTPStatus.OK, response_model=models.ResponseProcessLoginModel)
async def process_login_view(
    request: Request, payload: models.RequestProcessLoginModel = Body(...)
):
    """
    Вход администратора/Агентства (представителя)/Агента
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


@router.post(
    "/login-as",
    status_code=HTTPStatus.OK,
    response_model=models.ResponseProcessLoginModel,
)
async def superuser_auth_as_user_view(
    user_id: int = Query(..., alias="user"),
    payload: models.RequestSuperuserLoginModel = Body(...),
):
    """
    Получение токена для авторизации суперюзера под выбранным пользователем по кукам админки.
    """
    superuser_auth_as_user_case: use_cases.SuperuserAuthAsUserCase = use_cases.SuperuserAuthAsUserCase(
        token_creator=security.create_access_token,
        user_repo=users_repos.UserRepo,
        site_config=site_config,
    )
    return await superuser_auth_as_user_case(user_id=user_id, payload=payload)
