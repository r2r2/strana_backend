from fastapi import APIRouter, status, Path, Query, Depends

from common import dependencies, paginations, email
from common.settings.repos import AddServiceSettingsRepo
from src.notifications import (
    repos as notifications_repos,
    services as notification_services,
)
from src.users import constants as users_constants
from ..repos import (
    AdditionalServiceCategoryRepo as CategoryRepo,
    AdditionalServiceRepo as ServiceRepo,
    AdditionalServiceTypeRepo as ServiceTypeRepo,
    AdditionalServiceConditionStepRepo as StepRepo,
    AdditionalServiceTicketRepo as TicketRepo,
    AdditionalServiceTemplatetRepo as TemplateRepo,
    AdditionalServiceGroupStatusRepo as GroupStatusRepo,
)
from ..use_cases import (
    GetSpecCase,
    CategoriesAndServicesListCase,
    ServiceDetailCase,
    CreateTicketCase,
    TicketListCase,
    GetFacetCase,
)
from ..models import (
    ServiceSpecsResponse,
    ServiceFacetsResponse,
    ServicesByTypeResponse,
    ServiceDetailResponse,
    CreateTicketRequest,
    CreatedTicketResponse,
    TicketListResponse,
)


router = APIRouter(prefix="/add-services", tags=["Доп. услуги"])


@router.get(
    "/specs",
    status_code=status.HTTP_200_OK,
    response_model=ServiceSpecsResponse,
    dependencies=[
        Depends(dependencies.CurrentUserId(user_type=users_constants.UserType.CLIENT)),
    ],
)
async def spec_view():
    resources: dict = dict(
        category_repo=CategoryRepo,
    )
    get_specs: GetSpecCase = GetSpecCase(**resources)
    return await get_specs()


@router.get(
    "",
    status_code=status.HTTP_200_OK,
    response_model=list[ServicesByTypeResponse],
    dependencies=[
        Depends(dependencies.CurrentUserId(user_type=users_constants.UserType.CLIENT)),
    ],
)
async def service_list_view(category_id: int | None = Query(None, alias="categoryId")):
    """
    Список услуг по категориям
    """
    resources: dict = dict(
        service_repo=ServiceRepo,
        service_type_repo=ServiceTypeRepo,
    )
    get_categories: CategoriesAndServicesListCase = CategoriesAndServicesListCase(
        **resources
    )
    return await get_categories(category_id=category_id)


@router.get(
    "/facets", status_code=status.HTTP_200_OK, response_model=ServiceFacetsResponse
)
async def ticket_facet_list_view(
    user_id: int = Depends(
        dependencies.CurrentUserId(user_type=users_constants.UserType.CLIENT)
    ),
):
    """
    Фасеты заявок
    """
    resources: dict = dict(category_repo=CategoryRepo)
    facet_list: GetFacetCase = GetFacetCase(**resources)
    return await facet_list(user_id=user_id)


@router.get(
    "/tickets", status_code=status.HTTP_200_OK, response_model=TicketListResponse
)
async def ticket_list_view(
    category_id: int | None = Query(None, alias="categoryId"),
    pagination: paginations.PagePagination = Depends(
        dependencies.Pagination(page_size=20)
    ),
    user_id: int = Depends(
        dependencies.CurrentUserId(user_type=users_constants.UserType.CLIENT)
    ),
):
    """
    Список заявок
    """
    resources: dict = dict(
        ticket_repo=TicketRepo,
        template_repo=TemplateRepo,
        group_status_repo=GroupStatusRepo,
    )
    ticket_list: TicketListCase = TicketListCase(**resources)
    return await ticket_list(
        category_id=category_id, user_id=user_id, pagination=pagination
    )


@router.get(
    "/{serviceId}",
    status_code=status.HTTP_200_OK,
    response_model=ServiceDetailResponse,
    dependencies=[
        Depends(dependencies.CurrentUserId(user_type=users_constants.UserType.CLIENT)),
    ],
)
async def service_detail_view(service_id: int = Path(..., alias="serviceId")):
    """
    Деталка для услуги
    """
    resources: dict = dict(
        service_repo=ServiceRepo,
        step_repo=StepRepo,
    )
    get_service: ServiceDetailCase = ServiceDetailCase(**resources)
    return await get_service(service_id=service_id)


@router.post(
    "", status_code=status.HTTP_201_CREATED, response_model=CreatedTicketResponse
)
async def create_ticket_view(
    payload: CreateTicketRequest,
    user_id: int = Depends(
        dependencies.CurrentUserId(user_type=users_constants.UserType.CLIENT)
    ),
):
    """
    Создание заявки
    """
    get_email_template_service: notification_services.GetEmailTemplateService = (
        notification_services.GetEmailTemplateService(
            email_template_repo=notifications_repos.EmailTemplateRepo
        )
    )
    resources: dict = dict(
        ticket_repo=TicketRepo,
        group_status_repo=GroupStatusRepo,
        add_service_settings_repo=AddServiceSettingsRepo,
        email_class=email.EmailService,
        get_email_template_service=get_email_template_service,
    )
    create_ticket: CreateTicketCase = CreateTicketCase(**resources)
    return await create_ticket(user_id=user_id, payload=payload)
