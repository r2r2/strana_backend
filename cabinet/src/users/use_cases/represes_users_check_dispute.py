import asyncio
from datetime import datetime
from typing import Any, Type

from common import email
from config import site_config
from pytz import UTC
from src.admins.repos import AdminRepo
from src.agents.exceptions import AgentNotFoundError
from src.represes.repos import RepresRepo
from src.users.constants import UserType

from ..constants import UserStatus
from ..entities import BaseCheckCase
from src.users.exceptions import CheckNotFoundError, UserNotFoundError, UniqueStatusNotFoundError
from ..models import RequestAgentsUsersCheckDisputeModel
from src.users.repos import Check, CheckRepo, User, UserRepo, UniqueStatus, UniqueStatusRepo, HistoricalDisputeDataRepo
from src.notifications.services import GetEmailTemplateService


class RepresCheckDisputeCase(BaseCheckCase):
    mail_event_slug = "repres_check_dispute"

    def __init__(
        self,
        check_repo: Type[CheckRepo],
        email_class: Type[email.EmailService],
        repres_repo: Type[RepresRepo],
        user_repo: Type[UserRepo],
        admin_repo: Type[AdminRepo],
        unique_status_repo: Type[UniqueStatusRepo],
        historical_dispute_repo: Type[HistoricalDisputeDataRepo],
        email_recipients: dict,
        get_email_template_service: GetEmailTemplateService,
    ) -> None:
        self.check_repo = check_repo()
        self.email_class = email_class
        self.repres_repo = repres_repo()
        self.user_repo = user_repo()
        self.admin_repo = admin_repo()
        self.unique_status_repo: UniqueStatusRepo = unique_status_repo()
        self.historical_dispute_repo: HistoricalDisputeDataRepo = historical_dispute_repo()
        self.strana_manager = email_recipients['strana_manager']
        self.lk_site_host = site_config['site_host']
        self.get_email_template_service = get_email_template_service

    async def __call__(self, dispute_repres_id: int, payload: RequestAgentsUsersCheckDisputeModel) -> Check:
        data: dict[str:int] = payload.dict(exclude_unset=True)
        filters: dict[str:Any] = dict(id=data["user_id"])
        user: User = await self.user_repo.retrieve(filters=filters)
        if not user:
            raise UserNotFoundError
        repres: User = await self.repres_repo.retrieve(
            filters=dict(id=dispute_repres_id), prefetch_fields=["agency__city"]
        )
        if not repres:
            raise AgentNotFoundError
        filters: dict[str:Any] = dict(
            user_id=data["user_id"],
            status__in=[UserStatus.NOT_UNIQUE, UserStatus.CAN_DISPUTE],
        )
        check: Check = await self.check_repo.retrieve(filters=filters, ordering='-id')
        if not check:
            raise CheckNotFoundError

        unique_status: UniqueStatus = await self._get_unique_status(slug=UserStatus.DISPUTE)
        data = dict(
            unique_status=unique_status,
            agent_id=user.agent_id,
            agency_id=user.agency_id,
            comment=payload.comment,
            dispute_agent_id=dispute_repres_id,
            dispute_requested=datetime.now(tz=UTC),
        )
        historical_data: dict[str:Any] = dict(
            unique_status=unique_status,
            agent_id=user.agent_id,
            client_agency_id=user.agency_id,
            dispute_agent_id=dispute_repres_id,
            dispute_requested=datetime.now(tz=UTC),
            dispute_agent_agency_id=repres.agency_id,
        )
        await asyncio.gather(
            self.check_repo.update(check, data=data),
            self.historical_dispute_repo.create(data=historical_data),
        )
        await check.refresh_from_db(fields=['status'])

        filters = dict(type=UserType.ADMIN, receive_admin_emails=True, users_cities=repres.agency.city.id)
        admins = await self.admin_repo.list(filters=filters)

        data: dict[str:Any] = dict(
            recipients=[admin.email for admin in admins],
            agent_name=f"{repres.name} {repres.patronymic} {repres.surname}",
            client_name=f"{user.name} {user.patronymic} {user.surname}",
            client_email=user.email,
            client_phone=user.phone,
            client_comment=payload.comment,
            dispute_link=self._generate_dispute_link(dispute_id=check.id)
        )
        await self._send_email(**data)
        return check

    async def _send_email(self, recipients: list[str], **context) -> asyncio.Task:
        """
        Отправка сообщения об оспаривании
        """
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
            email_service: email.EmailService = self.email_class(**email_options)
            return email_service.as_task()

    def _generate_dispute_link(self, dispute_id: int):
        return f"https://{self.lk_site_host}/admin/disputes/dispute/{dispute_id}/change/"

    async def _get_unique_status(self, slug: str) -> UniqueStatus:
        """
        Получаем статус закрепления по slug
        """
        status: UniqueStatus = await self.unique_status_repo.retrieve(filters=dict(slug=slug))
        if not status:
            raise UniqueStatusNotFoundError
        return status
