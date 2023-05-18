from asyncio import Task
from datetime import datetime
from typing import Any, Type

from common import email
from config import site_config
from pytz import UTC
from src.admins.repos import AdminRepo
from src.agents.exceptions import AgentNotFoundError
from src.agents.repos import AgentRepo
from src.users.constants import UserType

from ..constants import UserStatus
from ..entities import BaseCheckCase
from ..exceptions import CheckNotFoundError, UserNotFoundError
from ..models import RequestAgentsUsersCheckDisputeModel
from ..repos import Check, CheckRepo, User, UserRepo


class CheckDisputeCase(BaseCheckCase):
    template: str = "src/users/templates/check_dispute.html"

    def __init__(
            self,
            check_repo: Type[CheckRepo],
            email_class: Type[email.EmailService],
            agent_repo: Type[AgentRepo],
            user_repo: Type[UserRepo],
            admin_repo: Type[AdminRepo],
            email_recipients: dict,
    ) -> None:
        self.check_repo = check_repo()
        self.email_class = email_class
        self.agent_repo = agent_repo()
        self.user_repo = user_repo()
        self.admin_repo = admin_repo()
        self.strana_manager = email_recipients['strana_manager']
        self.lk_site_host = site_config['site_host']

    async def __call__(self, dispute_agent_id: int, payload: RequestAgentsUsersCheckDisputeModel) -> Check:
        data: dict[str:int] = payload.dict(exclude_unset=True)
        filters: dict[str:Any] = dict(id=data["user_id"])
        user: User = await self.user_repo.retrieve(filters=filters)
        if not user:
            raise UserNotFoundError
        agent: User = await self.agent_repo.retrieve(filters=dict(id=dispute_agent_id, is_approved=True))
        if not agent:
            raise AgentNotFoundError
        filters: dict[str:Any] = dict(user_id=data["user_id"],
                                      status__in=[UserStatus.NOT_UNIQUE, UserStatus.CAN_DISPUTE])
        check: Check = await self.check_repo.retrieve(filters=filters, ordering='-id')
        if not check:
            raise CheckNotFoundError

        data = dict(
            status=UserStatus.DISPUTE,
            agent_id=user.agent_id,
            agency_id=user.agency_id,
            comment=payload.comment,
            dispute_agent_id=dispute_agent_id,
            dispute_requested=datetime.now(tz=UTC),
        )
        await self.check_repo.update(check, data=data)
        await check.refresh_from_db(fields=['status'])

        filters = dict(type=UserType.ADMIN, receive_admin_emails=True)
        admins = await self.admin_repo.list(filters=filters)

        data: dict[str:Any] = dict(
            recipients=[admin.email for admin in admins],
            agent_name=f"{agent.name} {agent.patronymic} {agent.surname}",
            client_name=f"{user.name} {user.patronymic} {user.surname}",
            client_email=user.email,
            client_phone=user.phone,
            client_comment=payload.comment,
            dispute_link=self._generate_dispute_link(dispute_id=check.id)
        )
        await self._send_email(**data)
        return check

    async def _send_email(self, recipients: list[str], **context) -> Task:
        """
        Отправка сообщения об оспаривании
        """
        email_options: dict[str, Any] = dict(
            topic="Проверка на уникальность оспорена",
            template=self.template,
            recipients=recipients,
            context=context
        )
        email_service: email.EmailService = self.email_class(**email_options)
        return email_service.as_task()

    def _generate_dispute_link(self, dispute_id: int):
        return f"https://{self.lk_site_host}/admin/disputes/dispute/{dispute_id}/change/"
