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

__all__ = ('admins_bookings_specs_view', 'admins_bookings_facets_views', 'admins_bookings_lookup_view',
           'admins_booking_retrieve_view', 'admins_bookings_list_view')


@router.get(
    "/admin/bookings/specs",
    status_code=HTTPStatus.OK,
    response_model=models.ResponseBookingSpecs,
    dependencies=[Depends(dependencies.CurrentUserId(user_type=users_constants.UserType.ADMIN))],
)
async def admins_bookings_specs_view():
    """
    Спеки пользователей администратором
    """
    resources: dict[str, Any] = dict(booking_repo=booking_repos.BookingRepo)
    admins_users_specs = use_cases.BookingsSpecsCase(**resources)
    return await admins_users_specs()


@router.get(
    "/admin/bookings/facets",
    status_code=HTTPStatus.OK,
    response_model=models.ResponseBookingFacets,
    dependencies=[Depends(dependencies.CurrentUserId(user_type=users_constants.UserType.ADMIN))],
)
async def admins_bookings_facets_views(
    init_filters: dict[str, Any] = Depends(filters.BookingUserFilter.filterize),
):
    """
    Фасеты пользователей администратором
    """
    resources: dict[str, Any] = dict(booking_repo=booking_repos.BookingRepo)
    admins_users_facets = use_cases.BookingsFacetsCase(**resources)
    return await admins_users_facets(init_filters=init_filters)


@router.get(
    "/admin/bookings/lookup",
    status_code=HTTPStatus.OK,
    response_model=models.ResponseBookingUsersLookupModel,
    dependencies=[Depends(dependencies.CurrentUserId(user_type=users_constants.UserType.ADMIN))],
)
async def admins_bookings_lookup_view(
    lookup: str = Query(str(), alias="search"),
    init_filters: dict[str, Any] = Depends(filters.BookingUserFilter.filterize),
):
    """
    Поиск пользователей администратором
    """
    resources: dict[str, Any] = dict(repo=booking_repos.BookingRepo)
    admins_users_lookup = use_cases.AdminBookingsLookupCase(
        **resources
    )
    return await admins_users_lookup(lookup=lookup, init_filters=init_filters)


@router.get(
    "/admin/bookings",
    status_code=HTTPStatus.OK,
    response_model=models.ResponseBookingsUsersListModel,
    dependencies=[Depends(dependencies.CurrentUserId(user_type=users_constants.UserType.ADMIN))],
)
async def admins_bookings_list_view(
    init_filters: dict[str, Any] = Depends(filters.BookingUserFilter.filterize),
    pagination: paginations.PagePagination = Depends(dependencies.Pagination()),
):
    """
    Сделки администратором
    """
    resources: dict[str, Any] = dict(
        user_repo=users_repos.UserRepo,
        check_repo=users_repos.CheckRepo,
        booking_repo=booking_repos.BookingRepo,
        amocrm_group_status_repo=AmocrmGroupStatusRepo,
        user_type=users_constants.UserType.ADMIN,
    )
    admins_users_list: use_cases.UsersBookingsCase = use_cases.UsersBookingsCase(**resources)
    return await admins_users_list(pagination=pagination, init_filters=init_filters)


@router.get(
    "/admin/bookings/{booking_id}",
    status_code=HTTPStatus.OK,
    response_model=models.users_bookings_list.ResponseUserResponseBookingRetrieve,
    # dependencies=[Depends(dependencies.CurrentUserId(user_type=users_constants.UserType.ADMIN))],
)
async def admins_booking_retrieve_view(
    booking_id: int = Path(...),
):
    from fastapi import HTTPException
    from datetime import datetime
    from pytz import UTC
    from src.booking.repos import BookingRepo, Booking
    from src.booking.constants import BookingSubstages
    # from src.notifications.repos import BookingNotificationRepo, BookingNotification
    from tortoise.query_utils import Q
    from src.cities.repos import CityRepo, City
    from src.amocrm.repos import AmocrmGroupStatusRepo
    from tortoise.queryset import QuerySet

    city: City = await CityRepo().retrieve(filters=dict(name__iexact='Москва'))
    print(f'{city=}')
    print(f'{city.name=}')


    # bookings: list[Booking] = await BookingRepo().list(
    #     filters=dict(
    #         # id=booking_id,
    #         price_payed=False,
    #         amocrm_status__group_status__is_final=False,
    #         expires__gt=datetime.now(tz=UTC),
    #     ),
    #     prefetch_fields=["project", "building"],
    # )
    # print(f"{bookings=}")
    # print(f'{len(bookings)=}')
    #
    # for booking in bookings:
    #
    #     time_left = booking.expires - datetime.now(tz=UTC)
    #
    #     total_seconds_left: int = int(time_left.total_seconds())
    #     if total_seconds_left < 0:
    #         hours, minutes = 0, 0
    #     else:
    #         hours, remainder_seconds = divmod(total_seconds_left, 3600)
    #         minutes, _ = divmod(remainder_seconds, 60)
    #
    #     print(f'{hours=}, {minutes=}')
    #     print(f'{hours:02}:{minutes:02}')
    #     time_difference = booking.expires - datetime.now(tz=UTC)
    #     if time_difference.total_seconds() < 0:
    #         # Booking has expired
    #         time_left = "00ч00м"
    #     else:
    #         time_left = (datetime.min + time_difference).strftime('%H:%M')
    #     print(f'{time_left=}')
        # print(f'Time left: {hours} hours and {minutes} minutes')

    # notification_conditions: list[BookingNotification] = await BookingNotificationRepo().list(
    #     related_fields=["sms_template"],
    #     prefetch_fields=["project"],
    # )
    # for condition in notification_conditions:
    #     print(f'{condition=}')
    #
    #     projects = [await project for project in condition.project]
    #     print(f'{projects=}')
    #
    # print(f"{notification_conditions=}")

    raise HTTPException(status_code=418)
    """
    Карточка бронирования для админа
    """
    resources: dict[str, Any] = dict(
        check_repo=users_repos.CheckRepo,
        amocrm_group_status_repo=AmocrmGroupStatusRepo,
        booking_repo=booking_repos.BookingRepo,
        agent_repo=agents_repos.AgentRepo,
        user_pinning_repo=users_repos.UserPinningStatusRepo,
    )
    booking_retrieve: use_cases.UserBookingRetrieveCase = use_cases.UserBookingRetrieveCase(**resources)
    return await booking_retrieve(booking_id=booking_id)
