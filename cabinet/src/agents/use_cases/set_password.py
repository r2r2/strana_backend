from pytz import UTC
from asyncio import Task
from datetime import datetime
from secrets import token_urlsafe
from typing import Callable, Any, Type

from ..entities import BaseAgentCase
from ..models import RequestSetPasswordModel
from ..repos import AgentRepo, User
from ..types import AgentSession, AgentHasher, AgentEmail
from ..exceptions import (
    AgentNotFoundError,
    AgentSamePasswordError,
    AgentPasswordTimeoutError,
    AgentChangePasswordError,
)
from src.users.loggers.wrappers import user_changes_logger


class SetPasswordCase(BaseAgentCase):
    """
    Установка пароля
    """

    template: str = "src/agents/templates/confirm_email_short.html"
    link: str = "https://{}/confirm/agents/confirm_email?q={}&p={}"

    def __init__(
        self,
        user_type: str,
        session: AgentSession,
        site_config: dict[str, Any],
        agent_repo: Type[AgentRepo],
        session_config: dict[str, Any],
        email_class: Type[AgentEmail],
        hasher: Callable[..., AgentHasher],
        token_creator: Callable[[int], str],
    ):
        self.hasher: AgentHasher = hasher()
        self.agent_repo: AgentRepo = agent_repo()
        self.agent_update = user_changes_logger(
            self.agent_repo.update, self, content="Установка пароля агенту"
        )

        self.user_type: str = user_type
        self.session: AgentSession = session
        self.email_class: Type[AgentEmail] = email_class
        self.token_creator: Callable[[int], str] = token_creator

        self.site_host: str = site_config["site_host"]
        self.password_settable_key: str = session_config["password_settable_key"]
        self.password_reset_key: str = session_config["password_reset_key"]

    async def __call__(self, payload: RequestSetPasswordModel) -> User:
        data: dict[str, Any] = payload.dict()
        password: str = data["password"]
        is_contracted: bool = data["is_contracted"]
        agent_id: int = await self.session.get(
            self.password_settable_key
        ) or await self.session.get(self.password_reset_key)
        filters = dict(
            id=agent_id,
            is_approved=True,
            type=self.user_type,
        )
        agent: User = await self.agent_repo.retrieve(filters=filters)
        if not agent:
            raise AgentNotFoundError
        if agent.password and agent.one_time_password:
            raise AgentChangePasswordError
        if self.hasher.verify(password, agent.one_time_password or agent.password):
            raise AgentSamePasswordError
        if agent.one_time_password:
            if not agent.reset_time or agent.reset_time < datetime.now(tz=UTC):
                raise AgentPasswordTimeoutError
        data = dict(
            reset_time=None,
            one_time_password=None,
            is_contracted=is_contracted,
            email_token=token_urlsafe(32),
            password=self.hasher.hash(password),
        )
        agent: User = await self.agent_update(agent, data=data)
        token: str = self.token_creator(agent.id)
        await self._send_email(agent=agent, token=token)

        await self.session.pop(self.password_settable_key)
        await self.session.pop(self.password_reset_key)
        return agent

    async def _send_email(self, agent: User, token: str) -> Task:
        confirm_link: str = self.link.format(self.site_host, token, agent.email_token)
        email_options: dict[str, Any] = dict(
            topic="Подтверждение почты",
            template=self.template,
            recipients=[agent.email],
            context=dict(confirm_link=confirm_link),
        )
        email_service: AgentEmail = self.email_class(**email_options)
        return email_service.as_task()
