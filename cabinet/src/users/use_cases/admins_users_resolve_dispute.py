from asyncio import Task
from typing import Type, Any, List

from common.email import EmailService
from src.users.entities import BaseCheckCase
from src.agents.exceptions import AgentNotFoundError
from ..constants import UserStatus
from ..exceptions import UserNotFoundError, CheckNotFoundError
from ..models import RequestAdminsUserCheckDispute
from src.users.repos import UserRepo, CheckRepo, Check, UniqueStatus
from src.users.utils import get_unique_status
from ...agents.repos import AgentRepo
from src.notifications.services import GetEmailTemplateService


class ResolveDisputeCase(BaseCheckCase):
    mail_event_slug = "resolve_check_dispute"

    def __init__(
        self,
        user_repo: Type[UserRepo],
        check_repo: Type[CheckRepo],
        email_class: Type[EmailService],
        agent_repo: Type[AgentRepo],
        get_email_template_service: GetEmailTemplateService,
    ):
        self.user_repo = user_repo()
        self.check_repo = check_repo()
        self.email_class = email_class
        self.agent_repo = agent_repo()
        self.get_email_template_service = get_email_template_service

    async def __call__(self, user_id: int, payload: RequestAdminsUserCheckDispute) -> Check:
        filters: dict[str:Any] = dict(id=user_id)
        user = await self.user_repo.retrieve(filters=filters)
        if not user:
            raise UserNotFoundError
        unique_status: UniqueStatus = await get_unique_status(slug=UserStatus.DISPUTE)
        filters: dict[str:Any] = dict(
            user_id=user_id,
            unique_status=unique_status,
        )
        check: Check = await self.check_repo.retrieve(
            filters=filters,
            ordering='-id',
            related_fields=["unique_status"],
        )
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

        new_status: UniqueStatus = await get_unique_status(slug=payload.status)
        data: dict[str:Any] = dict(
            unique_status=new_status,
        )
        await self.check_repo.update(check, data)
        return check

    async def _send_email(self, recipients: List[str], **context) -> Task:
        email_notification_template = await self.get_email_template_service(
            mail_event_slug=self.mail_event_slug,
            context=context,
        )

        if email_notification_template and email_notification_template.is_active:
            email_options: dict[str, Any] = dict(
                topic=email_notification_template.template_topic,
                content=email_notification_template.content,
                recipients=recipients,
                lk_type=email_notification_template.lk_type.value,
                mail_event_slug=email_notification_template.mail_event_slug,
            )
            email_service: EmailService = self.email_class(**email_options)
            return email_service.as_task()
