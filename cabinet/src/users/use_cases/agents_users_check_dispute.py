import asyncio
from datetime import datetime
from typing import Any

from pytz import UTC

from common import email
from config import amocrm_config, site_config
from src.admins.repos import AdminRepo
from src.agents.exceptions import AgentNotFoundError
from src.agents.repos import AgentRepo
from src.booking.repos import BookingRepo
from src.notifications.repos import RopEmailsDisputeRepo
from src.users.constants import UserStatus
from src.users.entities import BaseCheckCase
from src.users.exceptions import CheckNotFoundError, UserNotFoundError
from src.users.models import RequestAgentsUsersCheckDisputeModel
from src.users.repos import Check, CheckRepo, HistoricalDisputeDataRepo, UniqueStatus, User, UserRepo
from src.users.services import SendCheckAdminsEmailService
from src.users.utils import get_unique_status


class CheckDisputeCase(BaseCheckCase):
    mail_event_want_dispute_slug = "check_dispute"
    mail_event_want_work_slug = "check_dispute_want_work"
    want_dispute_slug = "want_dispute"
    want_work_slug = "want_work"

    def __init__(
        self,
        check_repo: type[CheckRepo],
        email_class: type[email.EmailService],
        agent_repo: type[AgentRepo],
        user_repo: type[UserRepo],
        admin_repo: type[AdminRepo],
        historical_dispute_repo: type[HistoricalDisputeDataRepo],
        rop_email_dispute_repo: type[RopEmailsDisputeRepo],
        booking_repo: type[BookingRepo],
        email_recipients: dict,
        send_check_admins_email: SendCheckAdminsEmailService,
    ) -> None:
        self.check_repo = check_repo()
        self.email_class = email_class
        self.agent_repo = agent_repo()
        self.user_repo = user_repo()
        self.admin_repo = admin_repo()
        self.historical_dispute_repo: HistoricalDisputeDataRepo = historical_dispute_repo()
        self.rop_email_dispute_repo: RopEmailsDisputeRepo = rop_email_dispute_repo()
        self.booking_repo: BookingRepo = booking_repo()
        self.strana_manager = email_recipients['strana_manager']
        self.lk_site_host = site_config['site_host']
        self.amocrm_host = amocrm_config["url"]
        self.send_check_admins_email = send_check_admins_email

    async def __call__(
        self,
        dispute_agent_id: int,
        payload: RequestAgentsUsersCheckDisputeModel,
    ) -> Check:
        data: dict[str:Any] = payload.dict(exclude_unset=True)
        filters: dict[str:Any] = dict(id=data["user_id"])
        user: User = await self.user_repo.retrieve(filters=filters)
        if not user:
            raise UserNotFoundError
        agent: User = await self.agent_repo.retrieve(
            filters=dict(id=dispute_agent_id, is_approved=True),
            prefetch_fields=["agency"],
        )
        if not agent:
            raise AgentNotFoundError
        filters: dict[str:Any] = dict(
            user_id=data["user_id"],
            unique_status__slug__in=[UserStatus.NOT_UNIQUE, UserStatus.CAN_DISPUTE],
        )
        check: Check = await self.check_repo.retrieve(
            filters=filters,
            ordering='-id',
            related_fields=['unique_status', 'project', 'project__city'],
        )
        if not check:
            raise CheckNotFoundError
        dispute_status: UniqueStatus = await get_unique_status(slug=UserStatus.DISPUTE)
        data = dict(
            unique_status=dispute_status,
            agent_id=user.agent_id,
            agency_id=user.agency_id,
            comment=payload.comment,
            dispute_agent_id=dispute_agent_id,
            dispute_requested=datetime.now(tz=UTC),
            button_pressed=True
        )
        historical_data: dict[str:Any] = dict(
            agent_id=user.agent_id,
            client=user,
            unique_status=dispute_status,
            client_agency_id=user.agency_id,
            dispute_agent_id=dispute_agent_id,
            dispute_requested=datetime.now(tz=UTC),
            dispute_agent_agency_id=agent.agency_id,
        )
        await asyncio.gather(
            self.check_repo.update(check, data=data),
            self.historical_dispute_repo.create(data=historical_data),
        )

        mail_data: dict[str:Any] = dict(
            agent_name=f"{agent.name if agent.name else ''}"
                       f"{' ' + agent.patronymic if agent.patronymic else ''}"
                       f"{' ' + agent.surname if agent.surname else ''}",
            client_name=f"{user.name if user.name else ''}"
                        f"{' ' + user.patronymic if user.patronymic else ''}"
                        f"{' ' + user.surname if user.surname else ''}",
            client_phone=user.phone,
            agent_phone=agent.phone,
            amocrm_link=self._generate_amocrm_link(check.amocrm_id),
            dispute_link=self._generate_dispute_link(dispute_id=check.id),
            client_comment=payload.comment,
            client_email=user.email,
        )

        if check.button_slug == self.want_dispute_slug:
            await self.send_check_admins_email(
                check=check,
                mail_event_slug=self.mail_event_want_dispute_slug,
                data=mail_data,
            )
        elif check.button_slug == self.want_work_slug:
            mail_data.update(dict(
                city=check.project.city.name,
                project=check.project.name,
            ))
            filters = dict(
                project_id=check.project.id,
            )
            rops = await self.rop_email_dispute_repo.list(filters=filters)
            await self.send_check_admins_email(
                check=check,
                mail_event_slug=self.mail_event_want_work_slug,
                data=mail_data,
                additional_recipients_emails=[rop.email for rop in rops],
            )

        return check

    def _generate_dispute_link(self, dispute_id: int):
        return f"https://{self.lk_site_host}/admin/disputes/dispute/{dispute_id}/change/"

    def _generate_amocrm_link(self, leads_id: int):
        """
        Example: https://eurobereg72.amocrm.ru/leads/detail/32152190
        """
        return f"{self.amocrm_host}/leads/detail/{leads_id}"
