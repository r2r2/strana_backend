from http import HTTPStatus
from typing import Any

from common import dependencies
from fastapi import APIRouter, Depends, Path, Query
from pydantic import Json, conint
from src.users import constants as users_constants
from src.users import filters, models
from src.users import repos as users_repos
from src.users import use_cases
from src.users.constants import DEFAULT_LIMIT

router = APIRouter(prefix="/customers", tags=["Customers"])


@router.get(
    "/lookup",
    status_code=HTTPStatus.OK,
    response_model=list[models.ResponseUserLookupModel],
    dependencies=[Depends(dependencies.DeletedUserCheck())],
)
async def clients_lookup(
    lookup: str = Query(str(), alias="search"),
    init_filters: dict[str, Any] = Depends(filters.UserFilter.filterize),
    limit: conint(ge=0) = Query(DEFAULT_LIMIT),
    offset: conint(ge=0) = Query(0),
    user_id: int = Depends(dependencies.CurrentInTypesUserId(user_types=[
        users_constants.UserType.AGENT,
        users_constants.UserType.REPRES,
        users_constants.UserType.ADMIN,
    ]
    )),
    agency_id: int = Depends(dependencies.CurrentUserExtra(key="agency_id")),
    user_type: str = Depends(dependencies.CurrentUserType()),
):
    """
    Поиск пользователей по части телефона и полного имени для агентов и представителей.
    """
    if user_type == users_constants.UserType.AGENT:
        resources: dict[str, Any] = dict(user_repo=users_repos.UserRepo)
        agents_users_lookup = use_cases.AgentCustomersLookupCase(**resources)
        return await agents_users_lookup(
            agent_id=user_id,
            lookup=lookup,
            init_filters=init_filters,
            limit=limit,
            offset=offset)
    elif user_type == users_constants.UserType.REPRES:
        resources: dict[str, Any] = dict(user_repo=users_repos.UserRepo)
        repres_users_lookup = use_cases.RepresCustomersLookupCase(**resources)
        return await repres_users_lookup(
            agency_id=agency_id,
            lookup=lookup,
            init_filters=init_filters,
            limit=limit,
            offset=offset,
        )
