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
    from datetime import datetime, timedelta
    from pytz import UTC
    from tortoise import Tortoise
    from config import tortoise_config
    from src.task_management import repos as task_management_repos
    from src.task_management import services
    from src.task_management.constants import PackageOfDocumentsSlug
    from common import amocrm
    from src.questionnaire import repos as questionnaire_repos
    # from src.agents import use_cases


    # resources: dict[str, Any] = dict(
    #     orm_class=Tortoise,
    #     orm_config=tortoise_config,
    #     task_instance_repo=task_management_repos.TaskInstanceRepo,
    #     task_status_repo=task_management_repos.TaskStatusRepo,
    #     booking_repo=booking_repos.BookingRepo,
    # )
    # update_status_service: services.UpdateTaskInstanceStatusService = services.UpdateTaskInstanceStatusService(
    #     **resources
    # )
    # status_slug = PackageOfDocumentsSlug.CHECK.value
    # await update_status_service(booking_id=booking_id, status_slug=status_slug)

    # resources: dict[str, Any] = dict(
    #     booking_repo=booking_repos.BookingRepo,
    #     upload_document_repo=questionnaire_repos.QuestionnaireUploadDocumentRepo,
    #     amocrm_class=amocrm.AmoCRM,
    #     update_task_instance_status_service=update_status_service,
    # )
    # send_upload_documents: use_cases.SendUploadDocumentsCase = use_cases.SendUploadDocumentsCase(**resources)
    # await send_upload_documents(booking_id=booking_id)
    # booking = await booking_repos.BookingRepo().retrieve(
    #     filters=dict(id=6490),
    #     related_fields=['user']
    # )
    # print(f'{(booking.expires - datetime.now(tz=UTC) - timedelta(seconds=10)).seconds=}')
    #
    # raise HTTPException(status_code=HTTPStatus.IM_A_TEAPOT, detail="I'm a teapot")
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
