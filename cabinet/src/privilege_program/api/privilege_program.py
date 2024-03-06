from http import HTTPStatus

from fastapi import APIRouter, status, Path, Query, Depends, HTTPException

from common import dependencies, email
from common.settings.repos import FeedbackSettingsRepo
from src.users import constants as users_constants
from ..exceptions import PrivilegeProgramNotFoundError
from ..models.programs import PrivilegeProgramDetailResponse
from ..models.specs import PrivilegeSpecsResponse
from ..models.request import CreatePrivilegeRequest, CreatedRequestResponse
from ..repos import (
    PrivilegeProgramRepo,
    PrivilegeCategoryRepo,
    PrivilegeRequestRepo,
    PrivilegeInfoRepo,
    PrivilegeBenefitRepo,
)
from ..use_cases import (
    GetSpecCase,
    ProgramListCase,
    ProgramDetailCase,
)
from src.notifications import (
    repos as notifications_repos,
    services as notification_services,
)
from ..models import ProgramByCategoryResponse, PrivilegeInfoResponse, PrivilegeBenefitResponse
from ..use_cases.create_request import CreateRequestCase
from ..use_cases.get_benefits import BenefitListCase
from ..use_cases.get_info import InfoListCase

router = APIRouter(prefix="/privilege-program", tags=["Программа привилегий"])


@router.get(
    "/specs",
    status_code=status.HTTP_200_OK,
    response_model=PrivilegeSpecsResponse,
)
async def spec_view(
        city: str | None = Query(
            default=None,
            description="Фильтр по городу",
            alias="city",
        ),
):
    resources: dict = dict(category_repo=PrivilegeCategoryRepo)
    get_specs: GetSpecCase = GetSpecCase(**resources)
    return await get_specs(city=city)


@router.get(
    "/info",
    status_code=status.HTTP_200_OK,
    response_model=list[PrivilegeInfoResponse],
)
async def info_list_view():
    """
    Список Общей информации
    """
    resources: dict = dict(
        info_repo=PrivilegeInfoRepo,
    )
    get_info: InfoListCase = InfoListCase(**resources)
    return await get_info()


@router.get(
    "/benefits",
    status_code=status.HTTP_200_OK,
    response_model=list[PrivilegeBenefitResponse],
)
async def benefits_list_view():
    """
    Список Преимуществ
    """
    resources: dict = dict(
        benefit_repo=PrivilegeBenefitRepo,
    )
    get_benefit: BenefitListCase = BenefitListCase(**resources)
    return await get_benefit()


@router.get(
    "/{programId}",
    status_code=status.HTTP_200_OK,
    response_model=PrivilegeProgramDetailResponse,
)
async def program_detail_view(program_slug: str = Path(..., alias="programId")):
    """
    Детальная карточка программы
    """
    resources: dict = dict(
        program_repo=PrivilegeProgramRepo,
    )
    get_program: ProgramDetailCase = ProgramDetailCase(**resources)

    try:
        program = await get_program(program_slug=program_slug)
    except PrivilegeProgramNotFoundError:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail="Privilege program not found")
    return program


@router.post(
    "/request", status_code=status.HTTP_201_CREATED,
    response_model=CreatedRequestResponse
)
async def create_request_view(
    payload: CreatePrivilegeRequest,
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
        request_repo=PrivilegeRequestRepo,
        feedback_settings_repo=FeedbackSettingsRepo,
        email_class=email.EmailService,
        get_email_template_service=get_email_template_service,
    )
    create_request_case: CreateRequestCase = CreateRequestCase(**resources)
    return await create_request_case(user_id=user_id, payload=payload)


@router.get(
    "",
    status_code=status.HTTP_200_OK,
    response_model=list[ProgramByCategoryResponse],
)
async def program_list_view(
        category_slugs: list[str] = Query(
            default=[],
            description="Фильтр по категориям",
            alias="categorySlug",
        ),
        city: str | None = Query(
            default=None,
            description="Фильтр по городу",
            alias="city",
        ),
):
    """
    Список программ по категориям
    """
    resources: dict = dict(
        program_repo=PrivilegeProgramRepo,
        category_repo=PrivilegeCategoryRepo,
    )
    get_programs: ProgramListCase = ProgramListCase(**resources)
    return await get_programs(category_slugs=category_slugs, city=city)
