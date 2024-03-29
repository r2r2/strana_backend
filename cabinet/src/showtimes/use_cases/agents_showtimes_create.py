from asyncio import Task

from pytz import UTC
from typing import Type, Any
from datetime import datetime

from ..entities import BaseShowTimeCase
from ..exceptions import ShowtimeNoClientError, ShowtimeNoProjectError
from ..models import RequestAgentsShowtimesCreateModel
from ..repos import ShowTimeRepo, ShowTime
from ..services import CreateShowTimeService
from ..types import ShowTimeUserRepo, ShowTimeUser, ShowTimeEmail, ShowTimeAgentRepo, ShowTimeProject, ShowTimeProjectRepo
from src.notifications.services import GetEmailTemplateService


class AgentsShowtimesCreateCase(BaseShowTimeCase):
    """
    Создание записи на показ агентом
    """
    eduard_email: str = "eduard.yarkaev@strana.com"
    regina_email: str = "regina.ramazanova@strana.com"

    mail_event_slug = "showtime"

    def __init__(
        self,
        user_types: Any,
        email_class: Type[ShowTimeEmail],
        user_repo: Type[ShowTimeUserRepo],
        showtime_repo: Type[ShowTimeRepo],
        project_repo: Type[ShowTimeProjectRepo],
        agent_repo: Type[ShowTimeAgentRepo],
        create_showtime_service: CreateShowTimeService,
        get_email_template_service: GetEmailTemplateService,
    ):
        self.user_repo: ShowTimeUserRepo = user_repo()
        self.agent_repo: ShowTimeAgentRepo = agent_repo()
        self.project_repo: ShowTimeProjectRepo = project_repo()
        self.showtime_repo: ShowTimeRepo = showtime_repo()

        self.user_types: Any = user_types
        self.email_class: ShowTimeEmail = email_class
        self.create_showtime_service: CreateShowTimeService = create_showtime_service
        self.get_email_template_service = get_email_template_service

    async def __call__(self, agent_id: int, payload: RequestAgentsShowtimesCreateModel) -> ShowTime:
        data: dict[str, Any] = payload.dict()
        phone: str = data.pop("phone")
        filters: dict[str, Any] = dict(phone=phone, type=self.user_types.CLIENT, agent_id=agent_id)
        user: ShowTimeUser = await self.user_repo.retrieve(filters=filters)
        filters: dict[str, Any] = dict(type=self.user_types.AGENT, id=agent_id)
        agent: ShowTimeUser = await self.agent_repo.retrieve(filters=filters)
        if not user or not agent:
            raise ShowtimeNoClientError
        project = None
        if payload.project_id:
            filters: dict[str, Any] = dict(id=payload.project_id)
            project: ShowTimeProject = await self.project_repo.retrieve(filters=filters)
            if not project:
                raise ShowtimeNoProjectError
        visit: datetime = data.pop("visit").replace(tzinfo=UTC)
        data: dict[str, Any] = dict(
            visit=visit,
            user_id=user.id,
            agent_id=agent_id,
            project_id=data.get("project_id"),
            property_type=data.get("property_type"),
        )
        showtime: ShowTime = await self.showtime_repo.create(data=data)
        if payload.project_id:
            await self.create_showtime_service(showtime_id=showtime.id)
        await self._send_client_email(client=user, agent=agent, date=visit, project=project)
        await self._send_agent_email(client=user, agent=agent, date=visit, project=project)
        await self._send_strana_emails(client=user, agent=agent, date=visit, project=project)
        return showtime

    async def _send_client_email(
        self, client: ShowTimeUser, agent: ShowTimeUser, date: datetime, project: ShowTimeProject
    ) -> Task:
        email_notification_template = await self.get_email_template_service(
            mail_event_slug=self.mail_event_slug,
            context=dict(content=None, agent=agent, date=date, project=project),
        )

        if email_notification_template and email_notification_template.is_active:
            email_options: dict[str, Any] = dict(
                topic=email_notification_template.template_topic,
                content=email_notification_template.content,
                recipients=[client.email],
                lk_type=email_notification_template.lk_type.value,
                mail_event_slug=email_notification_template.mail_event_slug,
            )
            email_service: ShowTimeEmail = self.email_class(**email_options)
            return email_service.as_task()

    async def _send_agent_email(
        self, client: ShowTimeUser, agent: ShowTimeUser, date: datetime, project: ShowTimeProject
    ) -> Task:
        email_notification_template = await self.get_email_template_service(
            mail_event_slug=self.mail_event_slug,
            context=dict(content=None, client=client, date=date, project=project),
        )

        if email_notification_template and email_notification_template.is_active:
            email_options: dict[str, Any] = dict(
                topic=email_notification_template.template_topic,
                content=email_notification_template.content,
                recipients=[agent.email],
                lk_type=email_notification_template.lk_type.value,
                mail_event_slug=email_notification_template.mail_event_slug,
            )
            email_service: ShowTimeEmail = self.email_class(**email_options)
            return email_service.as_task()

    async def _send_strana_emails(
        self, client: ShowTimeUser, agent: ShowTimeUser, date: datetime, project: ShowTimeProject
    ) -> Task:
        email_notification_template = await self.get_email_template_service(
            mail_event_slug=self.mail_event_slug,
            context=dict(content=None, client=client, agent=agent, date=date, project=project),
        )

        if email_notification_template and email_notification_template.is_active:
            email_options: dict[str, Any] = dict(
                topic=email_notification_template.template_topic,
                content=email_notification_template.content,
                recipients=[self.eduard_email, self.regina_email],
                lk_type=email_notification_template.lk_type.value,
                mail_event_slug=email_notification_template.mail_event_slug,
            )
            email_service: ShowTimeEmail = self.email_class(**email_options)
            return email_service.as_task()
