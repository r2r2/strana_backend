import asyncio
from datetime import datetime
from typing import Any, Type

from common import email
from config import site_config
from pytz import UTC
from src.admins.repos import AdminRepo
from src.agents.exceptions import AgentNotFoundError
from src.represes.repos import RepresRepo

from ..constants import UserStatus
from ..entities import BaseCheckCase
from src.users.exceptions import CheckNotFoundError, UserNotFoundError
from ..models import RequestAgentsUsersCheckDisputeModel
from src.users.repos import Check, CheckRepo, User, UserRepo, UniqueStatus, HistoricalDisputeDataRepo
from src.users.utils import get_unique_status
from src.users.services import SendCheckAdminsEmailService


class RepresCheckDisputeCase(BaseCheckCase):
    mail_event_slug = "repres_check_dispute"

    def __init__(
        self,
        check_repo: Type[CheckRepo],
        email_class: Type[email.EmailService],
        repres_repo: Type[RepresRepo],
        user_repo: Type[UserRepo],
        admin_repo: Type[AdminRepo],
        historical_dispute_repo: Type[HistoricalDisputeDataRepo],
        email_recipients: dict,
        send_check_admins_email: SendCheckAdminsEmailService,
    ) -> None:
        self.check_repo = check_repo()
        self.email_class = email_class
        self.repres_repo = repres_repo()
        self.user_repo = user_repo()
        self.admin_repo = admin_repo()
        self.historical_dispute_repo: HistoricalDisputeDataRepo = historical_dispute_repo()
        self.strana_manager = email_recipients['strana_manager']
        self.lk_site_host = site_config['site_host']
        self.send_check_admins_email = send_check_admins_email

    async def __call__(self, dispute_repres_id: int, payload: RequestAgentsUsersCheckDisputeModel) -> Check:
        data: dict[str:int] = payload.dict(exclude_unset=True)
        filters: dict[str:Any] = dict(id=data["user_id"])
        user: User = await self.user_repo.retrieve(filters=filters)
        if not user:
            raise UserNotFoundError
        repres: User = await self.repres_repo.retrieve(
            filters=dict(id=dispute_repres_id),
            prefetch_fields=["agency"],
        )
        if not repres:
            raise AgentNotFoundError
        filters: dict[str:Any] = dict(
            user_id=data["user_id"],
            unique_status__slug__in=[UserStatus.NOT_UNIQUE, UserStatus.CAN_DISPUTE],
        )
        check: Check = await self.check_repo.retrieve(
            filters=filters,
            ordering='-id',
            related_fields=['unique_status'],
        )
        if not check:
            raise CheckNotFoundError

        unique_status: UniqueStatus = await get_unique_status(slug=UserStatus.DISPUTE)
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
            client=user,
            client_agency_id=user.agency_id,
            dispute_agent_id=dispute_repres_id,
            dispute_requested=datetime.now(tz=UTC),
            dispute_agent_agency_id=repres.agency_id,
        )
        await asyncio.gather(
            self.check_repo.update(check, data=data),
            self.historical_dispute_repo.create(data=historical_data),
        )

        mail_data: dict[str:Any] = dict(
            agent_name=f"{repres.name} {repres.patronymic} {repres.surname}",
            client_name=f"{user.name} {user.patronymic} {user.surname}",
            client_email=user.email,
            client_phone=user.phone,
            client_comment=payload.comment,
            dispute_link=self._generate_dispute_link(dispute_id=check.id)
        )
        await self.send_check_admins_email(check=check, mail_event_slug=self.mail_event_slug, data=mail_data)
        return check

    def _generate_dispute_link(self, dispute_id: int):
        return f"https://{self.lk_site_host}/admin/disputes/dispute/{dispute_id}/change/"
