from secrets import token_urlsafe
from typing import Type, Any, Callable

from .base_proceed_changes import BaseProceedEmailChanges
from ..types import AgentEmail
from ..repos import AgentRepo, User
from ..models import RequestInitializeChangeEmail
from ..exceptions import AgentNotFoundError, AgentEmailTakenError
from src.notifications.services import GetEmailTemplateService


class InitializeChangeEmailCase(BaseProceedEmailChanges):
    """
    Обновление почты агентом
    """

    mail_event_slug: str = "agent_change_email"

    def __init__(
        self,
        user_type: str,
        agent_repo: Type[AgentRepo],
        site_config: dict[str, Any],
        email_class: Type[AgentEmail],
        token_creator: Callable[[int], str],
        get_email_template_service: GetEmailTemplateService,
    ) -> None:
        self.agent_repo: AgentRepo = agent_repo()
        self.user_type: str = user_type
        self.email_class: Type[AgentEmail] = email_class
        self.token_creator: Callable[[int], str] = token_creator
        self.site_host: str = site_config["site_host"]
        self.get_email_template_service: GetEmailTemplateService = get_email_template_service

    async def __call__(self, agent_id: int, payload: RequestInitializeChangeEmail) -> User:
        email = payload.email
        filters: dict[str, Any] = dict(id=agent_id, is_deleted=False, type=self.user_type)
        agent: User = await self.agent_repo.retrieve(filters=filters)
        if not agent:
            raise AgentNotFoundError
        filters: dict[str, Any] = dict(email__iexact=email)
        user: User = await self.agent_repo.retrieve(filters=filters)
        if user and user.id != agent.id:
            raise AgentEmailTakenError
        data = dict()
        data["change_email"]: str = email
        data["change_email_token"]: str = token_urlsafe(32)
        email_token: str = self.token_creator(agent.id)
        agent: User = await self.agent_repo.update(agent, data=data)
        await self._send_email(agent=agent, token=email_token)
        return agent
