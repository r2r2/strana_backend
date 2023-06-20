from http import HTTPStatus
from typing import Any, Callable, Coroutine

from common import dependencies, paginations
from fastapi import Depends, Path, Query
from src.amocrm.repos import AmocrmGroupStatusRepo
from src.booking import repos as booking_repos
from src.users import constants as users_constants
from src.users import filters, models
from src.users import repos as users_repos
from src.users import use_cases
from src.agents import repos as agents_repos

from ..user import router

__all__ = ('repres_bookings_specs_view', 'repres_bookings_facets_view', 'repres_bookings_lookup_view',
           'repres_bookings_list_view', 'repres_booking_retrieve_view')


@router.get(
    "/repres/bookings/specs",
    status_code=HTTPStatus.OK,
    response_model=models.ResponseBookingSpecs,
    dependencies=[
        Depends(dependencies.DeletedUserCheck()),
        Depends(dependencies.CurrentUserId(user_type=users_constants.UserType.REPRES)),
    ],
)
async def repres_bookings_specs_view(
    agency_id: int = Depends(dependencies.CurrentUserExtra(key="agency_id")),
):
    """
    Спеки пользователей представителя агентства
    """
    resources: dict[str, Any] = dict(booking_repo=booking_repos.BookingRepo)
    repres_users_specs = use_cases.BookingsSpecsCase(**resources)
    return await repres_users_specs(agency_id=agency_id)


@router.get(
    "/repres/bookings/facets",
    status_code=HTTPStatus.OK,
    response_model=models.ResponseBookingFacets,
    dependencies=[
        Depends(dependencies.DeletedUserCheck()),
        Depends(dependencies.CurrentUserId(user_type=users_constants.UserType.REPRES)),
    ],
)
async def repres_bookings_facets_view(
    init_filters: dict[str, Any] = Depends(filters.BookingUserFilter.filterize),
    agency_id: int = Depends(dependencies.CurrentUserExtra(key="agency_id")),
):
    """
    Фасеты пользователей представителя агентства
    """
    resources: dict[str, Any] = dict(booking_repo=booking_repos.BookingRepo)
    repres_users_facets = use_cases.BookingsFacetsCase(**resources)
    return await repres_users_facets(agency_id=agency_id, init_filters=init_filters)


@router.get(
    "/repres/bookings/lookup",
    status_code=HTTPStatus.OK,
    response_model=models.ResponseBookingUsersLookupModel,
    dependencies=[
        Depends(dependencies.DeletedUserCheck()),
        Depends(dependencies.CurrentUserId(user_type=users_constants.UserType.REPRES)),
    ],
)
async def repres_bookings_lookup_view(
    lookup: str = Query(str(), alias="search"),
    init_filters: dict[str, Any] = Depends(filters.BookingUserFilter.filterize),
    agency_id: int = Depends(dependencies.CurrentUserExtra(key="agency_id")),
):
    """
    Поиск пользователя представителя агентства
    """
    resources: dict[str, Any] = dict(repo=booking_repos.BookingRepo)
    repres_users_lookup = use_cases.RepresBookingsLookupCase(**resources)
    return await repres_users_lookup(agency_id=agency_id, lookup=lookup, init_filters=init_filters)


@router.get(
    "/repres/bookings",
    status_code=HTTPStatus.OK,
    response_model=models.ResponseBookingsUsersListModel,
    dependencies=[
        Depends(dependencies.DeletedUserCheck()),
        Depends(dependencies.CurrentUserId(user_type=users_constants.UserType.REPRES)),
    ],
)
async def repres_bookings_list_view(
    init_filters: dict[str, Any] = Depends(filters.BookingUserFilter.filterize),
    agency_id: int = Depends(dependencies.CurrentUserExtra(key="agency_id")),
    pagination: paginations.PagePagination = Depends(dependencies.Pagination()),
):
    """
    Сделки представителя агентства
    """
    resources: dict[str, Any] = dict(
        user_repo=users_repos.UserRepo,
        check_repo=users_repos.CheckRepo,
        booking_repo=booking_repos.BookingRepo,
        amocrm_group_status_repo=AmocrmGroupStatusRepo,
        user_type=users_constants.UserType.REPRES
    )
    repres_bookings_list: use_cases.UsersBookingsCase = use_cases.UsersBookingsCase(
        **resources
    )
    return await repres_bookings_list(agency_id=agency_id, init_filters=init_filters, pagination=pagination)


@router.get(
    "/repres/bookings/{booking_id}",
    status_code=HTTPStatus.OK,
    response_model=models.users_bookings_list.ResponseUserResponseBookingRetrieve,
)
async def repres_booking_retrieve_view(
    booking_id: int = Path(...),
    agency_id: int = Depends(dependencies.CurrentUserId(user_type=users_constants.UserType.REPRES)),
):
    """
    Карточка бронирования для представителя
    """
    resources: dict[str, Any] = dict(
        check_repo=users_repos.CheckRepo,
        amocrm_group_status_repo=AmocrmGroupStatusRepo,
        booking_repo=booking_repos.BookingRepo,
        agent_repo=agents_repos.AgentRepo,
        user_pinning_repo=users_repos.UserPinningStatusRepo,
    )
    booking_retrieve: use_cases.UserBookingRetrieveCase = use_cases.UserBookingRetrieveCase(**resources)
    return await booking_retrieve(booking_id=booking_id, agency_id=agency_id)
