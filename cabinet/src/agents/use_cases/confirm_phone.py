from typing import Type, Callable, Union, Any

from ..repos import AgentRepo, User
from ..entities import BaseAgentCase
from src.users.loggers.wrappers import user_changes_logger


class ConfirmPhoneCase(BaseAgentCase):
    """
    Подтверждение телефона
    """

    fail_link: str = "https://{}/account/agents/phone-confirmed"
    success_link: str = "https://{}/account/agents/phone-confirmed"

    def __init__(
        self,
        user_type: str,
        agent_repo: Type[AgentRepo],
        site_config: dict[str, Any],
        token_decoder: Callable[[str], Union[int, None]],
    ) -> None:
        self.agent_repo: AgentRepo = agent_repo()
        self.agent_update = user_changes_logger(
            self.agent_repo.update, self, content="Подтверждение телефона агента"
        )

        self.user_type: str = user_type
        self.token_decoder: Callable[[str], Union[int, None]] = token_decoder

        self.site_host: str = site_config["broker_site_host"]

    async def __call__(self, token: str, phone_token: str) -> str:
        agent_id: Union[int, None] = self.token_decoder(token)
        filters: dict[str, Any] = dict(
            id=agent_id, phone_token=phone_token, type=self.user_type, is_active=False
        )
        agent: User = await self.agent_repo.retrieve(filters=filters)
        link: str = self.fail_link.format(self.site_host)
        if agent:
            link: str = self.success_link.format(self.site_host)
            data: dict[str, Any] = dict(phone_token=None)
            if not agent.email_token:
                data["is_active"]: bool = True
            await self.agent_update(agent, data=data)
        return link
