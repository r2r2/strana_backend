from http import HTTPStatus
from typing import Any

from common import dependencies, paginations
from fastapi import Depends, Path, Query
from src.booking import repos as booking_repos
from src.properties import repos as properties_repos
from src.users import constants as users_constants
from src.users import filters, models
from src.users import repos as users_repos
from src.users import use_cases

from ..user import router

__all__ = (
    'repres_clients_specs_view', 'repres_clients_facets_view',
    'repres_clients_lookup_view', 'agent_clients_phone_lookup_view',
    'repres_clients_view', 'represes_users_retrieve_view', 'repres_agents_users_retrieve_view')


@router.get(
    "/repres/clients/specs",
    status_code=HTTPStatus.OK,
    response_model=models.ResponseClientSpecs,
    dependencies=[
        Depends(dependencies.DeletedUserCheck()),
        Depends(dependencies.CurrentUserId(user_type=users_constants.UserType.REPRES)),
    ],
)
async def repres_clients_specs_view(
    agency_id: int = Depends(dependencies.CurrentUserExtra(key="agency_id")),
):
    """
    Спеки пользователей представителя агентства
    """
    resources: dict[str, Any] = dict(user_repo=users_repos.UserRepo)
    repres_users_specs = use_cases.ClientsSpecsCase(**resources)
    return await repres_users_specs(agency_id=agency_id)


@router.get(
    "/repres/clients/facets",
    status_code=HTTPStatus.OK,
    response_model=models.ResponseClientFacets,
    dependencies=[
        Depends(dependencies.DeletedUserCheck()),
        Depends(dependencies.CurrentUserId(user_type=users_constants.UserType.REPRES)),
    ],
)
async def repres_clients_facets_view(
    init_filters: dict[str, Any] = Depends(filters.UserFilter.filterize),
    agency_id: int = Depends(dependencies.CurrentUserExtra(key="agency_id")),
):
    """
    Фасеты пользователей представителя агентства
    """
    resources: dict[str, Any] = dict(user_repo=users_repos.UserRepo)
    repres_users_facets = use_cases.ClientsFacetsCase(**resources)
    return await repres_users_facets(agency_id=agency_id, init_filters=init_filters)


@router.get(
    "/repres/clients/lookup",
    status_code=HTTPStatus.OK,
    response_model=models.ResponseAgentsUsersLookupModel,
    dependencies=[
        Depends(dependencies.DeletedUserCheck()),
        Depends(dependencies.CurrentUserId(user_type=users_constants.UserType.REPRES)),
    ],
)
async def repres_clients_lookup_view(
    lookup: str = Query(str(), alias="search"),
    init_filters: dict[str, Any] = Depends(filters.UserFilter.filterize),
    agency_id: int = Depends(dependencies.CurrentUserExtra(key="agency_id")),
):
    """
    Поиск пользователя представителя агентства
    """
    resources: dict[str, Any] = dict(user_repo=users_repos.UserRepo)
    repres_users_lookup = use_cases.RepresClientsLookupCase(**resources)
    return await repres_users_lookup(agency_id=agency_id, lookup=lookup, init_filters=init_filters)


@router.get(
    "/repres/clients/phone_lookup",
    status_code=HTTPStatus.OK,
    response_model=models.ResponseAgentsUsersPhoneLookupModel,
    dependencies=[
        Depends(dependencies.DeletedUserCheck()),
        Depends(dependencies.CurrentUserId(user_type=users_constants.UserType.REPRES)),
    ],
)
async def agent_clients_phone_lookup_view(
    phone: str = Query(str(), alias="search"),
    agency_id: int = Depends(dependencies.CurrentUserExtra(key="agency_id")),
):
    """
    Поиск пользователей агента по началу телефона
    """
    resources: dict[str, Any] = dict(user_repo=users_repos.UserRepo)
    repres_users_phone_lookup = use_cases.RepresClientsPhoneLookupCase(**resources)
    users = await repres_users_phone_lookup(agency_id=agency_id, phone=phone)
    return users


@router.get(
    "/repres/clients",
    response_model=models.ResponseClientsListModel
)
async def repres_clients_view(
    repres_id: int = Depends(dependencies.CurrentUserId(user_type=users_constants.UserType.REPRES)),
    init_filters: dict = Depends(filters.UserFilter.filterize),
    pagination: paginations.PagePagination = Depends(dependencies.Pagination()),
):
    """Список клиентов представителем"""
    resources: dict = dict(
        user_repo=users_repos.UserRepo,
        check_repo=users_repos.CheckRepo,
        user_pinning_repo=users_repos.UserPinningStatusRepo,
    )
    clients_case: use_cases.RepresListClientsCase = use_cases.RepresListClientsCase(**resources)
    return await clients_case(repres_id=repres_id, init_filters=init_filters, pagination=pagination)


@router.get(
    "/repres/clients/{user_id}",
    status_code=HTTPStatus.OK,
    response_model=models.ResponseClientRetrieveModel,
    dependencies=[
        Depends(dependencies.DeletedUserCheck()),
        Depends(dependencies.CurrentUserId(user_type=users_constants.UserType.REPRES)),
    ],
)
async def represes_users_retrieve_view(
    user_id: int = Path(...),
    agency_id: int = Depends(dependencies.CurrentUserExtra(key="agency_id")),
):
    """
    Пользователь представителя агентства
    """
    resources: dict[str, Any] = dict(
        user_repo=users_repos.UserRepo,
        check_repo=users_repos.CheckRepo,
        user_pinning_repo=users_repos.UserPinningStatusRepo,
    )
    represes_users_retrieve: use_cases.RepresesUsersRetrieveCase = (
        use_cases.RepresesUsersRetrieveCase(**resources)
    )
    return await represes_users_retrieve(agency_id=agency_id, user_id=user_id)


@router.get(
    "/repres/clients/{user_id}/{agent_id}",
    status_code=HTTPStatus.OK,
    response_model=models.ResponseRepresesAgentsUsersRetrieveModel,
    dependencies=[Depends(dependencies.CurrentUserId(user_type=users_constants.UserType.REPRES))],
)
async def repres_agents_users_retrieve_view(
    user_id: int = Path(...),
    agent_id: int = Path(...),
    agency_id: int = Depends(dependencies.CurrentUserExtra(key="agency_id")),
):
    """
    Пользователь агента представителя агентства
    """
    resources: dict[str, Any] = dict(
        user_repo=users_repos.UserRepo,
        check_repo=users_repos.CheckRepo,
        booking_repo=booking_repos.BookingRepo,
        property_repo=properties_repos.PropertyRepo,
    )
    represes_agents_users_retrieve: use_cases.RepresesAgentsUsersRetrieveCase = (
        use_cases.RepresesAgentsUsersRetrieveCase(**resources)
    )
    return await represes_agents_users_retrieve(user_id=user_id, agency_id=agency_id, agent_id=agent_id)
