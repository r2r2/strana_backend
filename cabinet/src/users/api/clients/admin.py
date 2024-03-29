from http import HTTPStatus
from typing import Any

from common import dependencies, paginations, amocrm
from common.email import email
from config import amocrm_config
from fastapi import Body, Depends, Path, Query
from src.agencies import repos as agencies_repos
from src.agents import repos as agents_repos
from src.booking import repos as booking_repos
from src.properties import repos as properties_repos
from src.users import constants as users_constants
from src.users import filters, models
from src.users import repos as users_repos
from src.users import use_cases
from src.users import services as user_services
from src.notifications import services as notification_services
from src.notifications import repos as notification_repos

from ..user import router

__all__ = ('admins_users_specs_view', 'admins_users_facets_views', 'admins_users_lookup_view', 'admin_clients_view',
           'admins_users_retrieve_view', 'admins_agents_users_retrieve_view', 'admins_users_update')


@router.get(
    "/admin/clients/specs",
    status_code=HTTPStatus.OK,
    response_model=models.ResponseClientSpecs,
    dependencies=[Depends(dependencies.CurrentUserId(user_type=users_constants.UserType.ADMIN))],
)
async def admins_users_specs_view():
    """
    Спеки пользователей администратором
    """
    admins_users_specs = use_cases.ClientsSpecsCase(
        user_repo=users_repos.UserRepo
    )
    return await admins_users_specs()


@router.get(
    "/admin/clients/facets",
    status_code=HTTPStatus.OK,
    response_model=models.ResponseClientFacets,
    dependencies=[Depends(dependencies.CurrentUserId(user_type=users_constants.UserType.ADMIN))],
)
async def admins_users_facets_views(
    init_filters: dict[str, Any] = Depends(filters.UserFilter.filterize),
):
    """
    Фасеты пользователей администратором
    """
    resources: dict[str, Any] = dict(user_repo=users_repos.UserRepo)
    admins_users_facets = use_cases.ClientsFacetsCase(**resources)
    return await admins_users_facets(init_filters=init_filters)


@router.get(
    "/admin/clients/lookup",
    status_code=HTTPStatus.OK,
    response_model=models.ResponseAdminsUsersLookupModel,
    dependencies=[Depends(dependencies.CurrentUserId(user_type=users_constants.UserType.ADMIN))],
)
async def admins_users_lookup_view(
    lookup: str = Query(str(), alias="search"),
    init_filters: dict[str, Any] = Depends(filters.UserFilter.filterize),
):
    """
    Поиск пользователей администратором
    """
    resources: dict[str, Any] = dict(user_repo=users_repos.UserRepo)
    admins_users_lookup = use_cases.AdminClientsLookupCase(
        **resources
    )
    return await admins_users_lookup(lookup=lookup, init_filters=init_filters)


@router.get(
    "/admin/clients",
    response_model=models.ResponseClientsListModel,
    dependencies=[Depends(dependencies.CurrentUserId(user_type=users_constants.UserType.ADMIN))],
)
async def admin_clients_view(
    init_filters: dict = Depends(filters.UserFilter.filterize),
    pagination: paginations.PagePagination = Depends(dependencies.Pagination()),
):
    """Список клиентов админом"""
    resources: dict = dict(
        user_repo=users_repos.UserRepo,
        check_repo=users_repos.CheckRepo,
        user_pinning_repo=users_repos.UserPinningStatusRepo,
    )
    clients_case: use_cases.AdminListClientsCase = use_cases.AdminListClientsCase(**resources)
    return await clients_case(init_filters=init_filters, pagination=pagination)


@router.get(
    "/admin/clients/{user_id}",
    status_code=HTTPStatus.OK,
    response_model=models.ResponseClientRetrieveModel,
    dependencies=[Depends(dependencies.CurrentUserId(user_type=users_constants.UserType.ADMIN))],
)
async def admins_users_retrieve_view(user_id: int = Path(...)):
    """
    Пользователь администратором
    """
    resources: dict[str, Any] = dict(
        user_repo=users_repos.UserRepo,
        check_repo=users_repos.CheckRepo,
        user_pinning_repo=users_repos.UserPinningStatusRepo,
    )
    admins_users_retrieve: use_cases.AdminsUsersRetrieveCase = use_cases.AdminsUsersRetrieveCase(
        **resources
    )
    return await admins_users_retrieve(user_id=user_id)


@router.get(
    "/admin/clients/{user_id}/{agent_id}",
    status_code=HTTPStatus.OK,
    response_model=models.ResponseAdminsAgentsUsersRetrieveModel,
    dependencies=[Depends(dependencies.CurrentUserId(user_type=users_constants.UserType.ADMIN))],
)
async def admins_agents_users_retrieve_view(user_id: int = Path(...), agent_id: int = Path(...)):
    """
    Пользователь агента администратором
    """
    resources: dict[str, Any] = dict(
        user_repo=users_repos.UserRepo,
        check_repo=users_repos.CheckRepo,
        booking_repo=booking_repos.BookingRepo,
        property_repo=properties_repos.PropertyRepo,
    )
    admins_agents_users_retrieve: use_cases.AdminsAgentsUsersRetrieveCase = (
        use_cases.AdminsAgentsUsersRetrieveCase(**resources)
    )
    return await admins_agents_users_retrieve(user_id=user_id, agent_id=agent_id)


@router.patch(
    "/admin/clients/{user_id}",
    status_code=HTTPStatus.NO_CONTENT,
    dependencies=[Depends(dependencies.CurrentUserId(user_type=users_constants.UserType.ADMIN))],
)
async def admins_users_update(
    user_id: int = Path(...),
    payload: models.RequestAdminsUsersUpdateModel = Body(...),
):
    """
    Обновление пользователя администратором
    """
    resources: dict[str, Any] = dict(
        amocrm_config=amocrm_config,
        amocrm_class=amocrm.AmoCRM,
        user_repo=users_repos.UserRepo,
        agent_repo=agents_repos.AgentRepo,
    )
    change_agent_service: user_services.ChangeAgentService = user_services.ChangeAgentService(**resources)

    get_email_template_service: notification_services.GetEmailTemplateService = \
        notification_services.GetEmailTemplateService(
            email_template_repo=notification_repos.EmailTemplateRepo,
        )

    resources: dict[str, Any] = dict(
        user_repo=users_repos.UserRepo,
        agent_repo=agents_repos.AgentRepo,
        agency_repo=agencies_repos.AgencyRepo,
        booking_repo=booking_repos.BookingRepo,
        change_agent_service=change_agent_service,
        get_email_template_service=get_email_template_service,
        email_class=email.EmailService,
    )
    admins_users_update_case: use_cases.AdminsUsersUpdateCase = use_cases.AdminsUsersUpdateCase(
        **resources
    )
    return await admins_users_update_case(user_id=user_id, payload=payload)
