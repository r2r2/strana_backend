from asyncio import Task
from secrets import token_urlsafe
from typing import Type, Callable, Union, Any

from ..entities import BaseAgentCase
from ..repos import AgentRepo, User
from ..types import AgentEmail
from src.users.loggers.wrappers import user_changes_logger


class ChangeEmailCase(BaseAgentCase):
    """
    Смена почты
    """

    template: str = "src/agents/templates/confirm_email.html"
    link: str = "https://{}/confirm/agents/confirm_email?q={}&p={}"

    fail_link: str = "https://{}/account/agents"
    success_link: str = "https://{}/account/agents"

    def __init__(
        self,
        user_type: str,
        agent_repo: Type[AgentRepo],
        site_config: dict[str, Any],
        email_class: Type[AgentEmail],
        token_creator: Callable[[int], str],
        token_decoder: Callable[[str], Union[int, None]],
    ) -> None:
        self.agent_repo: AgentRepo = agent_repo()
        self.agent_update = user_changes_logger(
            self.agent_repo.update, self, content="Смена почты агента"
        )

        self.email_class: Type[AgentEmail] = email_class
        self.token_creator: Callable[[int], str] = token_creator
        self.token_decoder: Callable[[str], Union[int, None]] = token_decoder

        self.user_type: str = user_type
        self.lk_site_host: str = site_config["lk_site_host"]
        self.broker_site_host: str = site_config["broker_site_host"]

    async def __call__(self, token: str, change_email_token: str) -> str:
        agent_id: Union[int, None] = self.token_decoder(token)
        filters: dict[str, Any] = dict(
            id=agent_id,
            is_active=True,
            is_approved=True,
            is_deleted=False,
            type=self.user_type,
            change_email_token=change_email_token,
        )
        agent: User = await self.agent_repo.retrieve(filters=filters)
        filters: dict[str, Any] = dict(email__iexact=agent.change_email)
        other_agent: User = await self.agent_repo.retrieve(filters=filters)
        link: str = self.fail_link.format(self.broker_site_host)
        if agent and not other_agent:
            data: dict[str, Any] = dict(
                is_active=False,
                change_email=None,
                change_email_token=None,
                email=agent.change_email,
                email_token=token_urlsafe(32),
            )
            token: str = self.token_creator(agent.id)
            await self.agent_update(agent, data=data)
            await self._send_email(agent=agent, token=token)
            link: str = self.success_link.format(self.broker_site_host)
        return link

    async def _send_email(self, agent: User, token: str) -> Task:
        confirm_link: str = self.link.format(self.lk_site_host, token, agent.email_token)
        email_options: dict[str, Any] = dict(
            topic="Подтверждение почты",
            recipients=[agent.email],
            template=self.template,
            context=dict(confirm_link=confirm_link),
        )
        email_service: AgentEmail = self.email_class(**email_options)
        return email_service.as_task()
