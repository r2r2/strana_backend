from secrets import token_urlsafe
from typing import Type, Any, Union, Callable

from .base_proceed_changes import BaseProceedPhoneChanges, BaseProceedEmailChanges
from ..types import AgentSms, AgentEmail
from ..repos import AgentRepo, User
from ..models import RequestAdminsAgentsUpdateModel
from ..exceptions import AgentNotFoundError, AgentPhoneTakenError, AgentEmailTakenError
from src.users.loggers.wrappers import user_changes_logger


class AdminsAgentsUpdateCase(BaseProceedPhoneChanges, BaseProceedEmailChanges):
    """
    Обновление агента администратором
    """

    def __init__(
        self,
        user_type: str,
        sms_class: Type[AgentSms],
        agent_repo: Type[AgentRepo],
        site_config: dict[str, Any],
        email_class: Type[AgentEmail],
        token_creator: Callable[[int], str],
    ) -> None:
        self.agent_repo: AgentRepo = agent_repo()
        self.agent_update = user_changes_logger(
            self.agent_repo.update, self, content="Обновление данных агента администратором"
        )

        self.user_type: str = user_type
        self.sms_class: Type[AgentSms] = sms_class
        self.email_class: Type[AgentEmail] = email_class
        self.token_creator: Callable[[int], str] = token_creator

        self.site_host: str = site_config["site_host"]

    async def __call__(self, agent_id: int, payload: RequestAdminsAgentsUpdateModel) -> User:
        data: dict[str, Any] = payload.dict()
        phone: Union[str, None] = data.pop("phone", None)
        email: Union[str, None] = data.pop("email", None)
        email_token = ""
        phone_token = ""
        filters: dict[str, Any] = dict(id=agent_id, is_deleted=False, type=self.user_type)
        agent: User = await self.agent_repo.retrieve(filters=filters)
        if not agent:
            raise AgentNotFoundError
        if phone:
            filters: dict[str, Any] = dict(phone=phone)
            user: User = await self.agent_repo.retrieve(filters=filters)
            if user and user.id != agent.id:
                raise AgentPhoneTakenError
        if email:
            filters: dict[str, Any] = dict(email__iexact=email)
            user: User = await self.agent_repo.retrieve(filters=filters)
            if user and user.id != agent.id:
                raise AgentEmailTakenError
        if phone:
            data["change_phone"]: str = phone
            data["change_phone_token"]: str = token_urlsafe(32)
            phone_token: str = self.token_creator(agent.id)
        if email:
            data["change_email"]: str = email
            data["change_email_token"]: str = token_urlsafe(32)
            email_token: str = self.token_creator(agent.id)
        agent: User = await self.agent_update(agent, data=data)
        if email:
            await self._send_email(agent=agent, token=email_token)
        if phone:
            await self._send_sms(agent=agent, token=phone_token)
        return agent
