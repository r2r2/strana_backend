from typing import Any

from fastapi import APIRouter, Depends, Path, Query, status

from common import dependencies, security
from src.booking import repos as booking_repos
from src.notifications import repos, models, use_cases
from src.projects import repos as project_repo
from src.text_blocks import models as text_block_models, repos as text_block_repos
from src.text_blocks.exceptions import TextBlockNotFoundError
from src.text_blocks.services import TextBlockHandlerService
from src.text_blocks.use_cases import TextBlockCase
from src.users import (
    services as users_services,
    repos as users_repos,
    use_cases as users_use_cases,
)
from src.main_page import repos as main_page_repos, use_cases as main_page_use_cases

router = APIRouter(prefix="/templates", tags=["Templates"])


@router.get(
    "/assign/sms_text",
    status_code=status.HTTP_200_OK,
    response_model=models.ResponseSMSText | None,
    dependencies=[Depends(dependencies.CurrentAnyTypeUserId())],
)
async def sms_help_text(
    project_id: int = Query(..., description="ID интересующего ЖК"),
):
    """Текст для отправки смс"""
    resources: dict[str, Any] = dict(
        assign_client_template_repo=repos.AssignClientTemplateRepo,
        project_repo=project_repo.ProjectRepo,
    )
    use_case: use_cases.AssignSMSTextCase = use_cases.AssignSMSTextCase(**resources)
    return await use_case(project_id=project_id)


@router.get(
    "/assign/{slug}",
    status_code=status.HTTP_200_OK,
    response_model=models.ResponseUnassignText,
)
async def client_assign_templates_text(
    slug: str = Path(..., description="slug текстового блока (шаблона)"),
    token: str = Query(..., alias="t"),
    data: str = Query(..., alias="d"),
):
    """Текст для страницы открепления клиента от агента"""
    resources: dict[str, Any] = dict(
        user_repo=users_repos.UserRepo,
        hasher=security.get_hasher,
    )
    get_agent_client_service = users_services.GetAgentClientFromQueryService(**resources)

    resources: dict[str, Any] = dict(
        assign_client_template_repo=repos.AssignClientTemplateRepo,
        get_agent_client_service=get_agent_client_service,
    )
    use_case: users_use_cases.AssignUnassignTextCase = users_use_cases.AssignUnassignTextCase(**resources)
    return await use_case(slug=slug, token=token, data=data)


@router.get(
    "/{slug}",
    status_code=status.HTTP_200_OK,
    response_model=text_block_models.ResponseTextBlockModel,
)
async def get_text_block(
    user_id: int | None = Depends(dependencies.CurrentOptionalUserIdWithoutRole()),
    slug: str = Path(..., description="slug текстового блока (шаблона)"),
    agent_id: int = Query(default=None),
):
    """
    Апи для получения текстового блока по слагу.
    """
    resources: dict[str, Any] = dict(
        booking_repo=booking_repos.BookingRepo,
        users_repo=users_repos.UserRepo,
    )
    handlers_service: TextBlockHandlerService = TextBlockHandlerService(**resources)
    resources: dict[str, Any] = dict(
        text_block_repo=text_block_repos.TextBlockRepo,
        handlers_service=handlers_service,
    )

    get_text_block_case: TextBlockCase = TextBlockCase(**resources)

    main_page_text_resources: dict[str, Any] = dict(
        main_page_text_repo=main_page_repos.MainPageTextRepo,
    )
    main_page_text: main_page_use_cases.MainPageTextCase = main_page_use_cases.MainPageTextCase(
        **main_page_text_resources
    )

    try:
        return await get_text_block_case(
            slug=slug,
            user_id=user_id,
            agent_id=agent_id,
        )
    except TextBlockNotFoundError:
        return await main_page_text(slug=slug)


@router.get(
    "/payment/{slug}",
    status_code=status.HTTP_200_OK,
    response_model=models.PaymentPageResponse,
    dependencies=[Depends(dependencies.CurrentAnyTypeUserId())],
)
async def payment_template_view(
    slug: str = Path(..., description="slug шаблона оплаты"),
):
    """
    Получение шаблона для оплаты
    """

    resources: dict[str, Any] = dict(
        payment_page_repo=booking_repos.PaymentPageNotificationRepo,
    )
    get_payment_page: use_cases.PaymentPageCase = use_cases.PaymentPageCase(**resources)
    return await get_payment_page(slug=slug)
