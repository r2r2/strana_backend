from asyncio import Task
from secrets import token_urlsafe
from typing import Type, Any, Callable

from ..exceptions import AgentNotFoundError, AgentNotApprovedError
from ..models import RequestEmailResetModel
from ..repos import AgentRepo, User
from ..entities import BaseAgentCase
from ..types import AgentEmail
from src.users.loggers.wrappers import user_changes_logger


class EmailResetCase(BaseAgentCase):
    """
    Ссылка для сброса
    """

    template: str = "src/agents/templates/reset_password.html"
    link: str = "https://{}/reset/agents/reset_password?q={}&p={}"

    def __init__(
        self,
        user_type: str,
        agent_repo: Type[AgentRepo],
        site_config: dict[str, Any],
        email_class: Type[AgentEmail],
        token_creator: Callable[[int], str],
    ):
        self.agent_repo: AgentRepo = agent_repo()
        self.agent_update = user_changes_logger(
            self.agent_repo.update, self, content="Ссылка для сброса почты агента"
        )

        self.user_type: str = user_type
        self.email_class: Type[AgentEmail] = email_class
        self.token_creator: Callable[[int], str] = token_creator

        self.site_host: str = site_config["site_host"]

    async def __call__(self, payload: RequestEmailResetModel) -> User:
        data: dict[str, Any] = payload.dict()
        email: str = data["email"]
        filters: dict[str, Any] = dict(email__iexact=email, is_active=True, type=self.user_type)
        agent: User = await self.agent_repo.retrieve(filters=filters)
        if not agent:
            raise AgentNotFoundError
        if not agent.is_approved:
            raise AgentNotApprovedError
        token: str = self.token_creator(agent.id)
        data: dict[str, Any] = dict(discard_token=token_urlsafe(32))
        await self.agent_update(agent, data=data)
        await self._send_email(agent=agent, token=token)
        return agent

    async def _send_email(self, agent: User, token: str) -> Task:
        reset_link: str = self.link.format(self.site_host, token, agent.discard_token)
        email_options: dict[str, Any] = dict(
            topic="Сброс пароля",
            template=self.template,
            recipients=[agent.email],
            context=dict(reset_link=reset_link),
        )
        email_service: AgentEmail = self.email_class(**email_options)
        return email_service.as_task()
