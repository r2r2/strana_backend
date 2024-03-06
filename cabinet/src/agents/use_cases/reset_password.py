from asyncio import sleep, create_task
from datetime import datetime, timedelta
from typing import Type, Callable, Union, Any
from starlette.datastructures import URL

from pytz import UTC

from common.sentry.utils import send_sentry_log
from common.unleash.client import UnleashClient
from config.feature_flags import FeatureFlags
from ..entities import BaseAgentCase
from ..repos import AgentRepo, User
from ..types import AgentSession
from src.users.loggers.wrappers import user_changes_logger
from src.users.exceptions import UserResetPasswordLinkExpiredError


class ResetPasswordCase(BaseAgentCase):
    """
    Сброс пароля
    """
    fail_link = "https://{}/errors/link-expired"
    success_link: str = "https://{}/account/agents/set-password"
    login_link: str = "https://{}/login"

    def __init__(
        self,
        user_type: str,
        session: AgentSession,
        request_url: URL,
        auth_config: dict[str, Any],
        site_config: dict[str, Any],
        session_config: dict[str, Any],
        agent_repo: Type[AgentRepo],
        token_decoder: Callable[[str], Union[int, None]],
    ) -> None:
        self.agent_repo: AgentRepo = agent_repo()
        self.agent_update = user_changes_logger(
            self.agent_repo.update, self, content="Сброс пароля для агента"
        )

        self.user_type: str = user_type
        self.session: AgentSession = session
        self.current_reset_password_url = request_url
        self.token_decoder: Callable[[str], Union[int, None]] = token_decoder

        self.site_host: str = site_config["broker_site_host"]
        self.password_time: int = auth_config["password_time"]
        self.password_reset_key: str = session_config["password_reset_key"]

    async def __call__(self, token: str, discard_token: str) -> str:
        agent_id: Union[int, None] = self.token_decoder(token)
        filters: dict[str, Any] = dict(
            id=agent_id,
            type=self.user_type,
        )
        agent: User = await self.agent_repo.retrieve(filters=filters)
        link: str = self.fail_link.format(self.site_host)
        if agent:
            if discard_token != agent.discard_token:
                return link
            link: str = self.success_link.format(self.site_host)
            self.session[self.password_reset_key]: int = agent_id
            await self.session.insert()
            data: dict[str, Any] = dict(
                discard_token=None,
                reset_time=datetime.now(tz=UTC) + timedelta(minutes=self.password_time),
            )
            await self.agent_update(agent, data=data)
            create_task(self._remove_discard())
        return link

    async def _remove_discard(self) -> bool:
        await sleep(self.password_time * 60)
        discard_id: Union[int, None] = await self.session.get(self.password_reset_key)
        if discard_id is not None:
            await self.session.pop(self.password_reset_key)
        return True
