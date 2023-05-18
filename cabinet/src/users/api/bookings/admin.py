from http import HTTPStatus
from typing import Any, Callable, Coroutine

from common import dependencies, paginations
from fastapi import Depends, Path, Query
from src.amocrm.repos import AmocrmStatusRepo
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
    # dependencies=[Depends(dependencies.CurrentUserId(user_type=users_constants.UserType.ADMIN))],
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
        amocrm_status_repo=AmocrmStatusRepo,
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
    from src.task_management import repos as task_management_repos
    from src.task_management import services as task_management_services
    from src.task_management.constants import PaidBookingSlug
    from src.agencies import repos as agencies_repos
    from common.amocrm import AmoCRM
    from src.agencies.services import CreateOrganizationService

    # resources: dict[str, Any] = dict(
    #     amocrm_class=AmoCRM, agency_repo=agencies_repos.AgencyRepo
    # )
    # create_organization_service: CreateOrganizationService = (
    #     CreateOrganizationService(**resources)
    # )
    # await create_organization_service(agency_id=257)
    #
    # resources: dict[str, Any] = dict(
    #     task_instance_repo=task_management_repos.TaskInstanceRepo,
    #     task_status_repo=task_management_repos.TaskStatusRepo,
    #     task_chain_repo=task_management_repos.TaskChainRepo,
    #     booking_repo=booking_repos.BookingRepo,
    # )
    # create_task_instance_service = task_management_services.CreateTaskInstanceService(
    #     **resources
    # )
    # await create_task_instance_service(booking_ids=[booking_id])
    # resources: dict[str, Any] = dict(
    #     task_instance_repo=task_management_repos.TaskInstanceRepo,
    #     task_status_repo=task_management_repos.TaskStatusRepo,
    #     booking_repo=booking_repos.BookingRepo,
    # )
    # update_task_instance_status_service = task_management_services.UpdateTaskInstanceStatusService(
    #     **resources
    # )
    # await update_task_instance_status_service(booking_id=booking_id, status_slug=PaidBookingSlug.RE_BOOKING.value)
    raise HTTPException(status_code=418, detail="I'm a teapot")
    """
    Карточка бронирования для админа
    """
    resources: dict[str, Any] = dict(
        check_repo=users_repos.CheckRepo,
        amocrm_status_repo=AmocrmStatusRepo,
        booking_repo=booking_repos.BookingRepo,
        agent_repo=agents_repos.AgentRepo,
    )
    booking_retrieve: use_cases.UserBookingRetrieveCase = use_cases.UserBookingRetrieveCase(**resources)
    return await booking_retrieve(booking_id=booking_id)
