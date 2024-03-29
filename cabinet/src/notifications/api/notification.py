from typing import Any
from http import HTTPStatus
from fastapi import APIRouter, Depends, Path, Body, Query
from pydantic import conint

from common import email
from src.users import constants as users_constants
from src.notifications import models, use_cases
from src.notifications import repos as notifications_repos
from src.notifications import services as notification_services

from common import dependencies, paginations


router = APIRouter(prefix="/notifications", tags=["Notifications"])


@router.get("/onboarding", status_code=HTTPStatus.OK, response_model=list[models.OnboardingModel])
async def get_onboarding_list(
    user_id: int = Depends(dependencies.CurrentAnyTypeUserId()),
):
    resources = dict(
        onboarding_repo=notifications_repos.OnboardingRepo,
        onboarding_through_repo=notifications_repos.OnboardingUserThroughRepo,
    )
    get_onboarding_list = use_cases.GetOnboardingListCase(**resources)
    return await get_onboarding_list(user_id=user_id)


@router.patch("/onboarding/{onboarding_id}", status_code=HTTPStatus.OK)
async def update_onboarding(
    user_id: int = Depends(dependencies.CurrentAnyTypeUserId()),
    onboarding_id: int = Path(...),
):
    resources = dict(
        onboarding_through_repo=notifications_repos.OnboardingUserThroughRepo,
    )
    update_onboarding_list = use_cases.ReadOnboardingCase(**resources)
    await update_onboarding_list(user_id=user_id, onboarding_id=onboarding_id)


@router.get(
    "/agents", status_code=HTTPStatus.OK, response_model=models.ResponseAgentsNotificationsListModel
)
async def agents_notifications_list_view(
    agent_id: int = Depends(dependencies.CurrentUserId(user_type=users_constants.UserType.AGENT)),
    pagination: paginations.PagePagination = Depends(dependencies.Pagination(page_size=12)),
):
    """
    Список уведомления агента
    """
    resources: dict[str, Any] = dict(notification_repo=notifications_repos.NotificationRepo)
    agent_notifications_list: use_cases.AgentsNotificationsListCase = (
        use_cases.AgentsNotificationsListCase(**resources)
    )
    return await agent_notifications_list(agent_id=agent_id, pagination=pagination)


@router.patch(
    "/agents/{notification_id}",
    status_code=HTTPStatus.OK,
    response_model=models.ResponseAgentsNotificationsUpdateModel,
)
async def agents_notifications_update_view(
    notification_id: int = Path(...),
    payload: models.RequestAgentsNotificationsUpdateModel = Body(...),
    agent_id: int = Depends(dependencies.CurrentUserId(user_type=users_constants.UserType.AGENT)),
):
    """
    Обновления уведомления агента
    """
    resources: dict[str, Any] = dict(notification_repo=notifications_repos.NotificationRepo)
    agent_notifications_update: use_cases.AgentsNotificationsUpdateCase = (
        use_cases.AgentsNotificationsUpdateCase(**resources)
    )
    return await agent_notifications_update(
        agent_id=agent_id, notification_id=notification_id, payload=payload
    )


@router.get(
    "/clients",
    status_code=HTTPStatus.OK,
    response_model=models.ResponseClientNotificationsModel,
)
async def client_notifications_list_view(
    user_id: int = Depends(dependencies.CurrentUserId(user_type=users_constants.UserType.CLIENT)),
    limit: conint(ge=0, le=40) = Query(20),
    offset: conint(ge=0) = Query(0),
):
    """
    Уведомления пользователя по изменениям сделок.
    """
    client_notifications_list_case = use_cases.ClientNotificationsListCase(
        client_notification_repo=notifications_repos.ClientNotificationRepo
    )
    return await client_notifications_list_case(user_id=user_id, limit=limit, offset=offset)


@router.get(
    "/clients/specs",
    status_code=HTTPStatus.OK,
    response_model=models.ResponseClientNotificationsSpecsModel,
)
async def client_notifications_specs_view(
    user_id: int = Depends(dependencies.CurrentUserId(user_type=users_constants.UserType.CLIENT)),
):
    """
    Отметка оповещений, как прочитанных.
    """
    client_notifications_specs_case = use_cases.ClientNotificationsSpecsCase(
        client_notification_repo=notifications_repos.ClientNotificationRepo
    )
    return await client_notifications_specs_case(user_id=user_id)


@router.post(
    "/send_test_email",
    status_code=HTTPStatus.NO_CONTENT,
)
async def sending_test_email_view(payload: models.SendingTestEmailModel = Body(...)):
    """
    Тестовый апи для отправки писем (отладка шаблонов).
    """
    get_email_template_service: notification_services.GetEmailTemplateService = \
        notification_services.GetEmailTemplateService(
            email_template_repo=notifications_repos.EmailTemplateRepo,
        )
    resources: dict[str, Any] = dict(
        email_class=email.EmailService,
        get_email_template_service=get_email_template_service,
    )
    sending_test_email_case: use_cases.SendingTestEmailCase = use_cases.SendingTestEmailCase(**resources)
    return await sending_test_email_case(payload=payload)
