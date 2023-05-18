from typing import Type, Callable, Union, Any

from ..repos import AgentRepo, User
from ..entities import BaseAgentCase
from ..types import AgentEmail, AgentAdminRepo
from src.users.loggers.wrappers import user_changes_logger


class ConfirmEmailCase(BaseAgentCase):
    """
    Подтверждение email
    """

    fail_link: str = "https://{}/account/agents/email-confirmed"
    success_link: str = "https://{}/account/agents/email-confirmed"
    agents_link = "https://{}/agents"

    def __init__(
        self,
        user_type: str,
        admin_user_type: str,
        agent_repo: Type[AgentRepo],
        admin_repo: Type[AgentAdminRepo],
        email_class: Type[AgentEmail],
        site_config: dict[str, Any],
        token_decoder: Callable[[str], Union[int, None]],
    ) -> None:
        self.agent_repo: AgentRepo = agent_repo()
        self.agent_update = user_changes_logger(
            self.agent_repo.update, self, content="Подтверждение email агента"
        )
        self.admin_repo: AgentAdminRepo = admin_repo()
        self.email_class: Type[AgentEmail] = email_class

        self.user_type: str = user_type
        self.admin_user_type: str = admin_user_type
        self.token_decoder: Callable[[str], Union[int, None]] = token_decoder

        self.site_host: str = site_config["broker_site_host"]

    async def __call__(self, token: str, email_token: str) -> str:
        agent_id: Union[int, None] = self.token_decoder(token)
        filters: dict[str, Any] = dict(
            id=agent_id, email_token=email_token, type=self.user_type, is_active=True
        )
        agent: User = await self.agent_repo.retrieve(
            filters=filters, prefetch_fields=["agency__maintainer"]
        )
        link: str = self.fail_link.format(self.site_host)
        if agent:
            link: str = self.success_link.format(self.site_host)
            data: dict[str, Any] = dict(email_token=None)
            if not agent.phone_token:
                data["is_approved"]: bool = True
            await self.agent_update(agent, data=data)
        return link
