from secrets import token_urlsafe
from typing import Type, Any, Callable

from .base_proceed_changes import BaseProceedPhoneChanges
from ..types import AgentSms
from ..repos import AgentRepo, User
from ..models import RequestInitializeChangePhone
from ..exceptions import AgentNotFoundError, AgentPhoneTakenError
from src.users.loggers.wrappers import user_changes_logger
from src.notifications.services import GetSmsTemplateService


class InitializeChangePhoneCase(BaseProceedPhoneChanges):
    """
    Обновление телефона агентом
    """

    sms_event_slug = "agent_change_phone"

    def __init__(
        self,
        user_type: str,
        sms_class: Type[AgentSms],
        agent_repo: Type[AgentRepo],
        site_config: dict[str, Any],
        token_creator: Callable[[int], str],
        get_sms_template_service: GetSmsTemplateService,
    ) -> None:
        self.agent_repo: AgentRepo = agent_repo()
        self.agent_update = user_changes_logger(
            self.agent_repo.update, self, content="Смена номера телефона агента"
        )
        self.user_type: str = user_type
        self.sms_class: Type[AgentSms] = sms_class
        self.token_creator: Callable[[int], str] = token_creator
        self.site_host: str = site_config["site_host"]
        self.get_sms_template_service: GetSmsTemplateService = get_sms_template_service

    async def __call__(self, agent_id: int, payload: RequestInitializeChangePhone) -> User:
        phone = payload.phone
        filters: dict[str, Any] = dict(id=agent_id, is_deleted=False, type=self.user_type)
        agent: User = await self.agent_repo.retrieve(filters=filters)
        if not agent:
            raise AgentNotFoundError
        filters: dict[str, Any] = dict(phone=phone)
        user: User = await self.agent_repo.retrieve(filters=filters)
        if user and user.id != agent.id:
            raise AgentPhoneTakenError

        data = dict()
        data["change_phone"]: str = phone
        data["change_phone_token"]: str = token_urlsafe(32)
        phone_token: str = self.token_creator(agent.id)
        agent: User = await self.agent_update(agent, data=data)
        await self._send_sms(agent=agent, token=phone_token)
        return agent
