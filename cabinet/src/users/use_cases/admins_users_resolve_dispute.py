from asyncio import Task
from typing import Type, Any, List

from common.email import EmailService
from src.users.entities import BaseCheckCase
from src.agents.exceptions import AgentNotFoundError
from ..constants import UserStatus
from ..exceptions import UserNotFoundError, CheckNotFoundError
from ..models import RequestAdminsUserCheckDispute
from ..repos import UserRepo, CheckRepo, Check
from ...agents.repos import AgentRepo


class ResolveDisputeCase(BaseCheckCase):
    template: str = "src/users/templates/resolve_check_dispute.html"

    def __init__(
            self,
            user_repo: Type[UserRepo],
            check_repo: Type[CheckRepo],
            email_class: Type[EmailService],
            agent_repo: Type[AgentRepo],
    ):
        self.user_repo = user_repo()
        self.check_repo = check_repo()
        self.email_class = email_class
        self.agent_repo = agent_repo()

    async def __call__(self, user_id: int, payload: RequestAdminsUserCheckDispute) -> Check:
        filters: dict[str:Any] = dict(id=user_id)
        user = await self.user_repo.retrieve(filters=filters)
        if not user:
            raise UserNotFoundError
        filters: dict[str:Any] = dict(
            user_id=user_id,
            status=UserStatus.DISPUTE
        )
        check: Check = await self.check_repo.retrieve(filters=filters, ordering='-id')
        if not check:
            raise CheckNotFoundError
        filters: dict[str:Any] = dict(
            id=check.dispute_agent_id
        )
        agent = await self.agent_repo.retrieve(filters=filters)
        if not agent:
            raise AgentNotFoundError

        email_data: dict[str:Any] = dict(
            recipients=[agent.email],
            client_phone=user.phone,
            approve=payload.status == UserStatus.UNIQUE,
            admin_comment=check.admin_comment
        )
        await self._send_email(**email_data)

        data: dict[str:Any] = dict(
            status=payload.status
        )
        await self.check_repo.update(check, data)
        await check.refresh_from_db(fields=['status'])

        return check

    async def _send_email(self, recipients: List[str], **context) -> Task:
        email_options: dict[str, Any] = dict(
            topic="Запрос на пересмотр статуса уникальности",
            template=self.template,
            recipients=recipients,
            context=context
        )
        email_service: EmailService = self.email_class(**email_options)
        return email_service.as_task()