from asyncio import Task
from typing import Type, Any

from ..repos import AgentRepo, User
from ..entities import BaseAgentCase
from ..exceptions import AgentNotFoundError
from ..models import RequestAdminsAgentsApprovalModel
from ..services import CreateContactService, EnsureBrokerTagService
from ..types import AgentEmail
from src.users.loggers.wrappers import user_changes_logger
from src.notifications.services import GetEmailTemplateService


class AdminsAgentsApprovalCase(BaseAgentCase):
    """
    Одобрение агента администратором
    """

    mail_event_slug: str = "agent_approval_email"
    login_link = "https://{}/account/agents/login"

    def __init__(
        self,
        user_type: str,
        import_clients_task: Any,
        agent_repo: Type[AgentRepo],
        site_config: dict[str, Any],
        email_class: Type[AgentEmail],
        create_contact_service: CreateContactService,
        ensure_broker_tag_service: EnsureBrokerTagService,
        get_email_template_service: GetEmailTemplateService,
    ) -> None:
        self.agent_repo: AgentRepo = agent_repo()
        self.agent_update = user_changes_logger(
            self.agent_repo.update, self, content="Одобрение агента администратором"
        )

        self.user_type: str = user_type
        self.email_class: Type[AgentEmail] = email_class
        self.import_clients_task: Any = import_clients_task
        self.create_contact_service: CreateContactService = create_contact_service
        self.ensure_broker_tag_service: EnsureBrokerTagService = ensure_broker_tag_service
        self.site_host: str = site_config["broker_site_host"]
        self.get_email_template_service: GetEmailTemplateService = get_email_template_service

    async def __call__(self, agent_id: int, payload: RequestAdminsAgentsApprovalModel) -> User:
        data: dict[str, Any] = payload.dict()
        filters: dict[str, Any] = dict(id=agent_id, type=self.user_type, is_deleted=False)
        agent: User = await self.agent_repo.retrieve(filters=filters)
        if not agent:
            raise AgentNotFoundError
        agent: User = await self.agent_update(agent, data=data)
        if not agent.is_imported:
            _, tags = await self.create_contact_service(agent=agent)
            setattr(agent, "tags", tags)
        await self.ensure_broker_tag_service(agent=agent)
        self.import_clients_task.delay(agent_id=agent_id)
        if agent.email and payload.is_approved:
            await self._send_email(agent=agent)
        return agent

    async def _send_email(self, agent: User) -> Task:
        login_link: str = self.login_link.format(self.site_host)
        email_notification_template = await self.get_email_template_service(
            mail_event_slug=self.mail_event_slug,
            context=dict(login_link=login_link),
        )

        if email_notification_template and email_notification_template.is_active:
            email_options: dict[str, Any] = dict(
                topic=email_notification_template.template_topic,
                content=email_notification_template.content,
                recipients=[agent.email],
                lk_type=email_notification_template.lk_type.value,
                mail_event_slug=email_notification_template.mail_event_slug,
            )
            email_service: AgentEmail = self.email_class(**email_options)
            return email_service.as_task()
