from typing import Any
from http import HTTPStatus
from fastapi import APIRouter, Depends, Body

from common import dependencies, email, amocrm

from src.users import repos as users_repos
from src.showtimes import models, use_cases, services
from src.showtimes import repos as showtimes_repos
from src.users import constants as users_constants
from src.agents import repos as agents_repos
from src.projects import repos as projects_repos
from src.notifications import services as notification_services
from src.notifications import repos as notification_repos

router = APIRouter(prefix="/showtimes", tags=["ShowTimes"])


@router.post("/agents", status_code=HTTPStatus.NO_CONTENT)
async def agents_showtimes_create(
    payload: models.RequestAgentsShowtimesCreateModel = Body(...),
    agent_id: int = Depends(dependencies.CurrentUserId(user_type=users_constants.UserType.AGENT)),
):
    """
    Создание записи на показ агентом
    """
    resources: dict[str, Any] = dict(amocrm_class=amocrm.AmoCRM, showtime_repo=showtimes_repos.ShowTimeRepo)
    create_showtime_service: services.CreateShowTimeService = services.CreateShowTimeService(**resources)
    get_email_template_service: notification_services.GetEmailTemplateService = \
        notification_services.GetEmailTemplateService(
            email_template_repo=notification_repos.EmailTemplateRepo,
        )
    resources: dict[str, Any] = dict(
        email_class=email.EmailService,
        user_repo=users_repos.UserRepo,
        agent_repo=agents_repos.AgentRepo,
        project_repo=projects_repos.ProjectRepo,
        user_types=users_constants.UserType,
        showtime_repo=showtimes_repos.ShowTimeRepo,
        create_showtime_service=create_showtime_service,
        get_email_template_service=get_email_template_service,
    )
    agents_showtimes_create: use_cases.AgentsShowtimesCreateCase = use_cases.AgentsShowtimesCreateCase(
        **resources
    )
    return await agents_showtimes_create(agent_id=agent_id, payload=payload)
