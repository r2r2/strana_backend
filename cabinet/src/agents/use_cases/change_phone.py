from asyncio import Task
from secrets import token_urlsafe
from typing import Type, Callable, Union, Any

from ..entities import BaseAgentCase
from ..repos import AgentRepo, User
from ..types import AgentSms
from src.users.loggers.wrappers import user_changes_logger


class ChangePhoneCase(BaseAgentCase):
    """
    Смена телефона
    """

    template: str = "Для подтверждения номера телефона перейдите по ссылке {confirm_link} . "
    link: str = "https://{}/confirm/agents/confirm_phone?q={}&p={}"

    fail_link: str = "https://{}/account/agents"
    success_link: str = "https://{}/account/agents"

    def __init__(
        self,
        user_type: str,
        agent_repo: Type[AgentRepo],
        site_config: dict[str, Any],
        sms_class: Type[AgentSms],
        token_creator: Callable[[int], str],
        token_decoder: Callable[[str], Union[int, None]],
    ) -> None:
        self.agent_repo: AgentRepo = agent_repo()
        self.agent_update = user_changes_logger(
            self.agent_repo.update, self, content="Смена телефона агента"
        )

        self.sms_class: Type[AgentSms] = sms_class
        self.token_creator: Callable[[int], str] = token_creator
        self.token_decoder: Callable[[str], Union[int, None]] = token_decoder

        self.user_type: str = user_type
        self.lk_site_host: str = site_config["lk_site_host"]
        self.broker_site_host: str = site_config["broker_site_host"]

    async def __call__(self, token: str, change_phone_token: str) -> str:
        agent_id: Union[int, None] = self.token_decoder(token)
        filters: dict[str, Any] = dict(
            id=agent_id,
            is_active=True,
            is_approved=True,
            is_deleted=False,
            type=self.user_type,
            change_phone_token=change_phone_token,
        )
        agent: User = await self.agent_repo.retrieve(filters=filters)
        filters: dict[str, Any] = dict(phone=agent.change_phone)
        other_agent: User = await self.agent_repo.retrieve(filters=filters)
        link: str = self.fail_link.format(self.broker_site_host)
        if agent and not other_agent:
            data: dict[str, Any] = dict(
                is_active=False,
                change_phone=None,
                change_phone_token=None,
                phone=agent.change_phone,
                phone_token=token_urlsafe(32),
            )
            token: str = self.token_creator(agent.id)
            await self.agent_update(agent, data=data)
            await self._send_sms(agent=agent, token=token)
            link: str = self.success_link.format(self.broker_site_host)
        return link

    async def _send_sms(self, agent: User, token: str) -> Task:
        confirm_link: str = self.link.format(self.lk_site_host, token, agent.change_phone_token)
        message: str = self.template.format(confirm_link=confirm_link)
        sms_options: dict[str, Any] = dict(phone=agent.phone, message=message)
        sms_service: AgentSms = self.sms_class(**sms_options)
        return sms_service.as_task()
