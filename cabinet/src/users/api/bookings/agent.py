from http import HTTPStatus
from typing import Any

from common import dependencies, paginations
from common.settings.repos import BookingSettingsRepo
from fastapi import Depends, Path, Query
from src.agents import repos as agents_repos
from src.amocrm.repos import AmocrmGroupStatusRepo
from src.booking import repos as booking_repos
from src.booking.repos import BookingTagRepo
from src.users import constants as users_constants
from src.users import filters, models
from src.users import repos as users_repos
from src.users import use_cases
from src.agents import repos as agents_repos
from src.users.api.user import router

__all__ = ('agents_bookings_specs_view', 'agents_bookings_facets_view', 'agents_bookings_lookup_view',
           'agents_booking_retrieve_view', 'agents_bookings_list_view')


@router.get(
    "/agent/bookings/specs",
    status_code=HTTPStatus.OK,
    response_model=models.ResponseBookingSpecs,
    dependencies=[Depends(dependencies.DeletedUserCheck())],
)
async def agents_bookings_specs_view(
    agent_id: int = Depends(dependencies.CurrentUserId(user_type=users_constants.UserType.AGENT)),
):
    """
    Спеки пользователей агента
    """
    resources: dict[str, Any] = dict(booking_repo=booking_repos.BookingRepo)
    agents_users_specs = use_cases.BookingsSpecsCase(**resources)
    return await agents_users_specs(agent_id=agent_id)


@router.get(
    "/agent/bookings/facets",
    status_code=HTTPStatus.OK,
    response_model=models.ResponseBookingFacets,
    dependencies=[Depends(dependencies.DeletedUserCheck())],
)
async def agents_bookings_facets_view(
    init_filters: dict[str, Any] = Depends(filters.BookingUserFilter.filterize),
    agent_id: int = Depends(dependencies.CurrentUserId(user_type=users_constants.UserType.AGENT)),
):
    """
    Фасеты пользователей агента
    """
    resources: dict[str, Any] = dict(booking_repo=booking_repos.BookingRepo)
    agents_users_facets = use_cases.BookingsFacetsCase(**resources)
    return await agents_users_facets(agent_id=agent_id, init_filters=init_filters)


@router.get(
    "/agent/bookings/lookup",
    status_code=HTTPStatus.OK,
    response_model=models.ResponseBookingUsersLookupModel,
    dependencies=[Depends(dependencies.DeletedUserCheck())],
)
async def agents_bookings_lookup_view(
    lookup: str = Query(str(), alias="search"),
    init_filters: dict[str, Any] = Depends(filters.BookingUserFilter.filterize),
    agent_id: int = Depends(dependencies.CurrentUserId(user_type=users_constants.UserType.AGENT)),
):
    """
    Поиск пользователя агента
    """
    resources: dict[str, Any] = dict(repo=booking_repos.BookingRepo)
    agents_users_search = use_cases.AgentBookingsLookupCase(
        **resources
    )
    return await agents_users_search(agent_id=agent_id, lookup=lookup, init_filters=init_filters)


@router.get(
    "/agent/bookings",
    status_code=HTTPStatus.OK,
    response_model=models.ResponseBookingsUsersListModel,
    dependencies=[Depends(dependencies.DeletedUserCheck())],
)
async def agents_bookings_list_view(
    init_filters: dict[str, Any] = Depends(filters.BookingUserFilter.filterize),
    pagination: paginations.PagePagination = Depends(dependencies.Pagination()),
    agent_id: int = Depends(dependencies.CurrentUserId(user_type=users_constants.UserType.AGENT)),
):
    """
    Сделки + клиенты агента
    """
    resources: dict[str, Any] = dict(
        user_repo=users_repos.UserRepo,
        booking_repo=booking_repos.BookingRepo,
        booking_tag_repo=booking_repos.BookingTagRepo,
        amocrm_group_status_repo=AmocrmGroupStatusRepo,
        user_type=users_constants.UserType.AGENT,
        booking_settings_repo=BookingSettingsRepo,
    )
    agents_users_list: use_cases.UsersBookingsCase = use_cases.UsersBookingsCase(**resources)
    return await agents_users_list(agent_id=agent_id, pagination=pagination, init_filters=init_filters)


@router.get(
    "/agent/bookings/{booking_id}",
    status_code=HTTPStatus.OK,
    response_model=models.users_bookings_list.ResponseUserResponseBookingRetrieve,
)
async def agents_booking_retrieve_view(
    booking_id: int = Path(...),
    agent_id: int = Depends(dependencies.CurrentUserId(user_type=users_constants.UserType.AGENT)),
):
    """
    Карточка бронирования для агента
    """
    resources: dict[str, Any] = dict(
        check_repo=users_repos.CheckRepo,
        amocrm_group_status_repo=AmocrmGroupStatusRepo,
        booking_repo=booking_repos.BookingRepo,
        agent_repo=agents_repos.AgentRepo,
        user_pinning_repo=users_repos.UserPinningStatusRepo,
        booking_settings_repo=BookingSettingsRepo,
        booking_tag_repo=BookingTagRepo,
    )
    booking_retrieve: use_cases.UserBookingRetrieveCase = \
        use_cases.UserBookingRetrieveCase(**resources)
    return await booking_retrieve(booking_id=booking_id, agent_id=agent_id)
