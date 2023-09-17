from http import HTTPStatus
from typing import Any

from common import dependencies, paginations
from fastapi import Depends, Path, Query
from src.users import constants as users_constants
from src.users import filters, models
from src.users import repos as users_repos
from src.users import use_cases
from src.users.api.user import router

__all__ = (
    'agent_clients_specs_view',
    'agent_clients_facets_view',
    'agent_clients_lookup_view',
    'agent_clients_view',
    'agents_users_retrieve_view',
)


@router.get(
    "/agent/clients/specs",
    status_code=HTTPStatus.OK,
    response_model=models.ResponseClientSpecs,
    dependencies=[Depends(dependencies.DeletedUserCheck())],
)
async def agent_clients_specs_view(
    agent_id: int = Depends(dependencies.CurrentUserId(user_type=users_constants.UserType.AGENT)),
):
    """
    Спеки пользователей агента
    """
    resources: dict[str, Any] = dict(user_repo=users_repos.UserRepo)
    agents_users_specs = use_cases.ClientsSpecsCase(**resources)
    return await agents_users_specs(agent_id=agent_id)


@router.get(
    "/agent/clients/facets",
    status_code=HTTPStatus.OK,
    response_model=models.ResponseClientFacets,
    dependencies=[Depends(dependencies.DeletedUserCheck())],
)
async def agent_clients_facets_view(
    init_filters: dict[str, Any] = Depends(filters.UserFilter.filterize),
    agent_id: int = Depends(dependencies.CurrentUserId(user_type=users_constants.UserType.AGENT)),
):
    """
    Фасеты пользователей агента
    """
    resources: dict[str, Any] = dict(user_repo=users_repos.UserRepo)
    agents_users_facets = use_cases.ClientsFacetsCase(**resources)
    return await agents_users_facets(agent_id=agent_id, init_filters=init_filters)


@router.get(
    "/agent/clients/lookup",
    status_code=HTTPStatus.OK,
    response_model=models.ResponseAgentsUsersLookupModel,
    dependencies=[Depends(dependencies.DeletedUserCheck())],
)
async def agent_clients_lookup_view(
    lookup: str = Query(str(), alias="search"),
    init_filters: dict[str, Any] = Depends(filters.UserFilter.filterize),
    agent_id: int = Depends(dependencies.CurrentUserId(user_type=users_constants.UserType.AGENT)),
):
    """
    Поиск пользователя агента
    """
    resources: dict[str, Any] = dict(user_repo=users_repos.UserRepo)
    agents_users_search = use_cases.AgentClientsLookupCase(**resources)
    return await agents_users_search(agent_id=agent_id, lookup=lookup, init_filters=init_filters)


@router.get(
    "/agent/clients",
    response_model=models.ResponseClientsListModel
)
async def agent_clients_view(
    init_filters: dict = Depends(filters.UserFilter.filterize),
    pagination: paginations.PagePagination = Depends(dependencies.Pagination()),
    agent_id: int = Depends(dependencies.CurrentUserId(user_type=users_constants.UserType.AGENT)),
):
    """Список клиентов агентом"""
    resources: dict = dict(
        user_repo=users_repos.UserRepo,
        check_repo=users_repos.CheckRepo,
        user_pinning_repo=users_repos.UserPinningStatusRepo,
    )
    clients_case: use_cases.AgentListClientsCase = use_cases.AgentListClientsCase(**resources)
    return await clients_case(agent_id=agent_id, init_filters=init_filters, pagination=pagination)


@router.get(
    "/agent/clients/{user_id}",
    status_code=HTTPStatus.OK,
    response_model=models.ResponseClientRetrieveModel,
    dependencies=[Depends(dependencies.DeletedUserCheck())],
)
async def agents_users_retrieve_view(
    user_id: int = Path(...),
    agent_id: int = Depends(dependencies.CurrentUserId(user_type=users_constants.UserType.AGENT)),
):
    """
    Пользователь агента
    """
    resources: dict[str, Any] = dict(
        user_repo=users_repos.UserRepo,
        check_repo=users_repos.CheckRepo,
        user_pinning_repo=users_repos.UserPinningStatusRepo,
    )
    agents_users_retrieve: use_cases.AgentsUsersRetrieveCase = use_cases.AgentsUsersRetrieveCase(
        **resources
    )
    return await agents_users_retrieve(user_id=user_id, agent_id=agent_id)
