import asyncio
from datetime import datetime
from typing import Any, Awaitable, Callable, Optional, Type

from pytz import UTC

from src.agents.types import AgentEmail
from src.booking.repos import BookingRepo
from src.users.constants import UserType
from src.users.entities import BaseUserCase
from src.users.exceptions import UserMissMatchError
from src.users.models import RequestUsersCheckModel
from src.users.repos import (
    Check,
    CheckHistoryRepo,
    CheckRepo,
    User,
    UserRepo,
    UserRoleRepo,
    AmoCrmCheckLogRepo, CheckHistory,
)
from src.users.services import SendCheckAdminsEmailService
from src.users.utils import get_unique_status_button


class UsersCheckCase(BaseUserCase):
    """
    Проверка клиента на уникальность
    """
    mail_event_slug: str = "check_admin_email"
    lead_url: str = "https://eurobereg72.amocrm.ru/leads/detail/{amocrm_id}"

    def __init__(
        self,
        user_repo: Type[UserRepo],
        user_role_repo: Type[UserRoleRepo],
        check_repo: Type[CheckRepo],
        history_check_repo: Type[CheckHistoryRepo],
        amocrm_history_check_log_repo: Type[AmoCrmCheckLogRepo],
        check_unique_service: Callable[..., Awaitable],
        booking_repo: Type[BookingRepo],
        email_class: Type[AgentEmail],
        send_check_admins_email: SendCheckAdminsEmailService,
    ) -> None:
        self.user_repo: UserRepo = user_repo()
        self.user_role_repo: UserRoleRepo = user_role_repo()
        self.check_repo: CheckRepo = check_repo()
        self.booking_repo: BookingRepo = booking_repo()
        self.history_check_repo: CheckHistoryRepo = history_check_repo()
        self.amocrm_history_check_log_repo: AmoCrmCheckLogRepo = amocrm_history_check_log_repo()
        self.check_unique_service: Callable[..., Awaitable] = check_unique_service
        self.email_class: Type[AgentEmail] = email_class
        self.send_check_admins_email = send_check_admins_email

    async def __call__(
        self,
        payload: RequestUsersCheckModel,
        agent_id: Optional[int] = None,
        agency_id: Optional[int] = None,
        user_id: Optional[int] = None
    ) -> Check:
        data: dict[str, Any] = payload.dict(exclude_unset=True)
        phone: str = data["phone"]
        filters: dict[str, Any] = dict(phone=phone, type=UserType.CLIENT)
        user: Optional[User] = await self.user_repo.retrieve(filters=filters, related_fields=["agent__agency"])

        if payload.email and not user:
            email: str = data["email"]
            filters: dict[str, Any] = dict(email__iexact=email, type=UserType.CLIENT)
            user: User = await self.user_repo.retrieve(filters=filters, related_fields=["agent__agency"])
            if user:
                raise UserMissMatchError

        if phone and not user:
            user_role = await self.user_role_repo.retrieve(filters=dict(slug=UserType.CLIENT))
            data: dict[str, Any] = dict(
                type=UserType.CLIENT,
                phone=phone,
                role=user_role,
            )
            user: User = await self.user_repo.create(data=data)

        check, history_check_logs_ids = await self._exist_user_check(
            user=user,
            phone=phone,
            agent_id=agent_id,
            agency_id=agency_id,
        )

        if not agency_id:
            agent_filters: dict = dict(id=agent_id)
            agent: dict = await self.user_repo.retrieve(filters=agent_filters).values("agency_id")
            agency_id: int = agent.get("agency_id")

        await check.fetch_related("unique_status", "user")
        history_check_data: dict = dict(
            client_id=user_id,
            agent_id=agent_id,
            agency_id=agency_id,
            client_phone=phone,
            unique_status=check.unique_status,
            term_uid=check.term_uid,
            term_comment=check.term_comment,
            lead_link=self.lead_url.format(amocrm_id=check.amocrm_id),
        )

        history_check: CheckHistory = await self.history_check_repo.create(data=history_check_data)

        filters = dict(id__in=history_check_logs_ids)
        data = dict(check_history=history_check)
        await self.amocrm_history_check_log_repo.bulk_update(filters=filters, data=data)

        if check.button_slug:
            check.button = await get_unique_status_button(slug=check.button_slug)

        return check

    async def _exist_user_check(
        self,
        user: User,
        phone: str,
        agent_id: Optional[int],
        agency_id: Optional[int],
    ) -> tuple[Check, list[int]]:
        """
        Проверяем уникальность в случае, когда пользователь есть в бд.
        Если не нашли привязанную к пользователю проверку - создаём новую.
        """
        history_check_logs_ids = []
        filters: dict[str, Any] = dict(user_id=user.id)
        check: Optional[Check] = await self.check_repo.retrieve(
            filters=filters,
            related_fields=["unique_status"],
            ordering='-id',
        )
        if not check:
            data: dict[str, Any] = dict(user_id=user.id, requested=datetime.now(tz=UTC))
            check: Check = await self.check_repo.create(data=data)
        if not check.status_fixed:
            history_check_logs_ids = await self.__update_check_status(
                phone=phone,
                check=check,
                user=user,
                agent_id=agent_id,
                agency_id=agency_id,
            )
        return check, history_check_logs_ids

    async def __update_check_status(
        self,
        phone: str,
        check: Check,
        user: Optional[User] = None,
        agent_id: Optional[int] = None,
        agency_id: Optional[int] = None,
        payload: Optional[dict[str, Any]] = None,
    ) -> list[int]:
        """
        Обновляем статус для проверки (Check) в амо.
        Сервис check_unique_service обновляет check.status внутри вызова.
        """
        _, history_check_logs_ids = await self.check_unique_service(phone=phone, check=check, user=user,
                                                                    agent_id=agent_id, agency_id=agency_id)
        await check.refresh_from_db()

        if check.send_admin_email:
            mail_data: dict[str, Any] = await self._prepare_email_data(
                phone=phone,
                user=user,
                agent_id=agent_id,
                payload=payload,
                agency_id=agency_id,
            )
            await self.send_check_admins_email(check=check, mail_event_slug=self.mail_event_slug, data=mail_data)
        return history_check_logs_ids

    async def _prepare_email_data(
        self,
        phone: str,
        user: Optional[User],
        agent_id: Optional[int] = None,
        agency_id: Optional[int] = None,
        payload: Optional[dict[str, Any]] = None,
    ) -> dict[str, Any]:
        """
        Подготавливаем данные для отправки письма администратору
        """
        fio_client: str = (
            f'{payload.get("surname", "")} '
            f'{payload.get("name", "")} '
            f'{payload.get("patronymic", "")}'
            .strip()
        ) if payload else ""

        # Ищем название агентства агента или репреза
        agent_agency: str = ''
        if agent_id:
            agent: Optional[User] = await self.user_repo.retrieve(
                filters=dict(id=agent_id, type=UserType.AGENT),
                related_fields=["agency"],
            )
            agent_agency: str = agent.agency.name if agent and agent.agency else ''

        if agency_id:
            repres: Optional[User] = await self.user_repo.retrieve(
                filters=dict(agency_id=agency_id, type=UserType.REPRES),
                related_fields=["agency"],
            )
            agent_agency: str = repres.agency.name if repres and repres.agency else ''

        # Подготавливаем данные для отправки письма администратору
        data: dict[str, Any] = dict(
            fio_client=user.full_name if user else fio_client,
            client_amocrm_id=user.amocrm_id if user else None,
            agent_agency=agent_agency,
            client_agency=user.agent.agency.name if user and user.agent and user.agent.agency else None,
            client_phone=phone,
        )
        return data
