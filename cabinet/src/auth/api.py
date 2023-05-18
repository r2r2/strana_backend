from http import HTTPStatus
from typing import Any

from common import security
from config import auth_config, session_config
from fastapi import APIRouter, Body, Request
from src.admins import repos as admins_repos
from src.users import constants as users_constants
from src.users import models, use_cases

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
        user_type=users_constants.UserType.ADMIN,
        token_creator=security.create_access_token,
    )
    process_login: use_cases.ProcessLoginCase = use_cases.ProcessLoginCase(**resources)
    return await process_login(payload=payload)
