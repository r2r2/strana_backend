from asyncio import Task
from secrets import token_urlsafe
from typing import Type, Callable, Union, Any

from ..entities import BaseAgentCase
from ..repos import AgentRepo, User
from ..types import AgentSms
from src.users.loggers.wrappers import user_changes_logger
from src.notifications.services import GetSmsTemplateService
from common.schemas import UrlEncodeDTO
from common.utils import generate_notify_url


class ChangePhoneCase(BaseAgentCase):
    """
    Смена телефона
    """

    sms_event_slug = "agent_confirm_change_phone"
    link_route_template: str = "/confirm/agents/confirm_phone"

    fail_link: str = "https://{}/account/agents"
    success_link: str = "https://{}/account/agents"
    common_link_route_template: str = "/account/agents"

    def __init__(
        self,
        user_type: str,
        agent_repo: Type[AgentRepo],
        site_config: dict[str, Any],
        sms_class: Type[AgentSms],
        token_creator: Callable[[int], str],
        token_decoder: Callable[[str], Union[int, None]],
        get_sms_template_service: GetSmsTemplateService,
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

        self.get_sms_template_service: GetSmsTemplateService = get_sms_template_service

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
        sms_notification_template = await self.get_sms_template_service(
            sms_event_slug=self.sms_event_slug,
        )
        if sms_notification_template and sms_notification_template.is_active:
            url_data: dict[str, Any] = dict(
                host=self.lk_site_host,
                route_template=self.link_route_template,
                query_params=dict(
                    q=token,
                    p=agent.change_phone_token,
                ),
                use_ampersand_ascii=True,
            )
            url_dto: UrlEncodeDTO = UrlEncodeDTO(**url_data)
            confirm_link: str = generate_notify_url(url_dto=url_dto)
            sms_options: dict[str, Any] = dict(
                phone=agent.phone,
                message=sms_notification_template.template_text.format(confirm_link=confirm_link),
                lk_type=sms_notification_template.lk_type.value,
                sms_event_slug=sms_notification_template.sms_event_slug,
            )
            sms_service: AgentSms = self.sms_class(**sms_options)
            return sms_service.as_task()
