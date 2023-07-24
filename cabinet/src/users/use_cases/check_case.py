import asyncio
from datetime import datetime
from typing import Any, Awaitable, Callable, Optional, Type

from pytz import UTC

from common.email import EmailService
from src.agents.types import AgentEmail
from src.booking.repos import Booking, BookingRepo
from src.cities.repos import City
from src.notifications.services import GetEmailTemplateService
from src.users.constants import UserType, UserStatus, UserPinningStatusType
from src.users.entities import BaseUserCase
from src.users.exceptions import UserMissMatchError, UniqueStatusNotFoundError
from src.users.models import RequestUsersCheckModel
from src.users.repos import (
    Check,
    CheckHistoryRepo,
    CheckRepo,
    HistoricalDisputeDataRepo,
    User,
    UserRepo,
    UniqueStatus,
    UniqueStatusRepo,
)


class UsersCheckCase(BaseUserCase):
    """
    Проверка клиента на уникальность
    """
    admin_email_slug: str = "check_admin_email"

    def __init__(
        self,
        user_repo: Type[UserRepo],
        check_repo: Type[CheckRepo],
        history_check_repo: Type[CheckHistoryRepo],
        unique_status_repo: Type[UniqueStatusRepo],
        historical_dispute_repo: Type[HistoricalDisputeDataRepo],
        check_unique_service: Callable[..., Awaitable],
        booking_repo: Type[BookingRepo],
        email_class: Type[AgentEmail],
        get_email_template_service: GetEmailTemplateService,
    ) -> None:
        self.user_repo: UserRepo = user_repo()
        self.check_repo: CheckRepo = check_repo()
        self.unique_status_repo: UniqueStatusRepo = unique_status_repo()
        self.booking_repo: BookingRepo = booking_repo()
        self.historical_dispute_repo: HistoricalDisputeDataRepo = historical_dispute_repo()

        self.history_check_repo: CheckHistoryRepo = history_check_repo()
        self.check_unique_service: Callable[..., Awaitable] = check_unique_service
        self.email_class: Type[AgentEmail] = email_class
        self.get_email_template_service: GetEmailTemplateService = get_email_template_service

        self.same_pinned: bool = False
        self.repres_pinned: bool = False
        self.agent_repres_pinned: bool = False

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
        if user:
            user_id = user.id
            await self._set_pinned_flags(user=user, agent_id=agent_id, agency_id=agency_id)

            check: Check = await self._exist_user_check(
                user=user,
                phone=phone,
                agent_id=agent_id,
                agency_id=agency_id,
            )

        else:
            check: Check = await self._not_exist_user_check(
                phone=phone,
                payload=data,
                agent_id=agent_id,
                agency_id=agency_id,
            )

        if not agency_id:
            agent_filters: dict = dict(id=agent_id)
            agent: dict = await self.user_repo.retrieve(filters=agent_filters).values("agency_id")
            agency_id: int = agent.get("agency_id")

        await check.fetch_related("unique_status")
        history_check_data: dict = dict(
            client_id=user_id,
            agent_id=agent_id,
            agency_id=agency_id,
            client_phone=phone,
            unique_status=check.unique_status,
        )

        dispute_agent = duspute_repres = None
        if agency_id:
            duspute_repres: Optional[User] = await self.user_repo.retrieve(
                filters=dict(agency_id=agency_id, type=UserType.REPRES)
            )
        if agent_id:
            dispute_agent: Optional[User] = await self.user_repo.retrieve(
                filters=dict(id=agent_id, type=UserType.AGENT)
            )
        historical_data: dict[str, Any] = dict(
            unique_status=check.unique_status,
            agent_id=agent_id,
            client_agency_id=user.agency_id if user else None,
            dispute_agent=dispute_agent or duspute_repres,
            dispute_requested=datetime.now(tz=UTC),
            dispute_agent_agency_id=agency_id or dispute_agent.agency_id,
        )
        await asyncio.gather(
            self.history_check_repo.create(data=history_check_data),
            self.historical_dispute_repo.create(data=historical_data),
        )
        return check

    async def _exist_user_check(
        self,
        user: User,
        phone: str,
        agent_id: Optional[int],
        agency_id: Optional[int],
    ) -> Check:
        """
        Проверяем уникальность в случае, когда пользователь есть в бд.
        Если не нашли привязанную к пользователю проверку - создаём новую.
        """
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
            await self.__update_check_status(
                phone=phone,
                check=check,
                user=user,
                agent_id=agent_id,
                agency_id=agency_id,
            )
        return check

    async def _not_exist_user_check(
        self,
        phone: str,
        payload: dict[str, Any],
        agent_id: Optional[int],
        agency_id: Optional[int],
    ) -> Check:
        """
        Проверка уникальности в случае, если юзера нет в бд.
        Мы не создаём пользователей в бд и амо до закрепления.
        Для корректного ответа создаём пустую проверку, без привязки к пользователю.
        """
        data: dict[str, Any] = dict(
            requested=datetime.now(tz=UTC),
        )
        check: Check = await self.check_repo.create(data)
        await self.__update_check_status(
            phone=phone,
            check=check,
            payload=payload,
            agent_id=agent_id,
            agency_id=agency_id,
        )
        return check

    async def __update_check_status(
        self,
        phone: str,
        check: Check,
        user: Optional[User] = None,
        agent_id: Optional[int] = None,
        agency_id: Optional[int] = None,
        payload: Optional[dict[str, Any]] = None,
    ) -> None:
        """
        Обновляем статус для проверки (Check) в амо.
        Сервис check_unique_service обновляет check.status внутри вызова.
        """
        await self.check_unique_service(phone=phone, check=check, user=user, agent_id=agent_id)
        await check.fetch_related("unique_status")

        unique_status: UniqueStatus = check.unique_status

        if unique_status.slug == UserStatus.UNIQUE:
            # Уникальный
            return

        elif unique_status.slug == UserStatus.NOT_UNIQUE:
            # Не уникальный
            if self.same_pinned:
                # Клиент закреплен за проверяющим агентом или представителем
                unique_status: UniqueStatus = await self._get_unique_status(slug=UserStatus.SAME_PINNED)

            elif self.agent_repres_pinned:
                # Агент проверяет клиента, закрепленного за другим агентом из этого же агентства
                unique_status: UniqueStatus = await self._get_unique_status(slug=UserStatus.AGENT_REPRES_PINNED)

        elif unique_status.slug == UserStatus.CAN_DISPUTE:
            # Закреплен, но можно оспорить
            if self.same_pinned:
                # Клиент закреплен за проверяющим агентом или представителем
                unique_status: UniqueStatus = await self._get_unique_status(slug=UserPinningStatusType.PARTIALLY_PINNED)

            elif self.repres_pinned:
                # Агент проверяет клиента, закрепленного за представителем из этого же агентства
                unique_status: UniqueStatus = await self._get_unique_status(slug=UserStatus.REPRES_PINNED_DISPUTE)

        if unique_status != check.unique_status:
            # Обновляем статус в бд
            await self.check_repo.update(check, data={"unique_status": unique_status})

        if check.send_admin_email:
            recipients: list[str] = await self._get_admin_recipients(check=check)
            if not recipients:
                return
            data: dict[str, Any] = await self._prepare_email_data(
                phone=phone,
                user=user,
                agent_id=agent_id,
                payload=payload,
                agency_id=agency_id,
            )
            await self._send_admin_email(recipients=recipients, data=data)

    async def _set_pinned_flags(
        self,
        user: User,
        agent_id: Optional[int] = None,
        agency_id: Optional[int] = None,
    ) -> None:
        """
        Устанавливаем флаги для проверки на то, что пользователь закреплён за агентом или агентством.
        """
        agent = repres = None
        if agent_id:
            agent: Optional[User] = await self.user_repo.retrieve(
                filters=dict(id=agent_id, type=UserType.AGENT)
            )
        if agency_id:
            repres: Optional[User] = await self.user_repo.retrieve(
                filters=dict(agency_id=agency_id, type=UserType.REPRES)
            )
        agent_pinned: bool = True if agent and agent.id == user.agent_id else False
        repres_pinned: bool = True if repres and repres.id == user.agent_id else False
        if agent_pinned or repres_pinned:
            # Клиент закреплен за проверяющим агентом или представителем
            self.same_pinned = True

        elif agent and user.agency_id == agent.agency_id and agent.agency_id is not None:
            if user.agent.type == UserType.AGENT:
                # Агент проверяет клиента, закрепленного за другим агентом из этого же агентства
                self.agent_repres_pinned = True
            elif user.agent.type == UserType.REPRES:
                # Агент проверяет клиента, закрепленного за представителем из этого же агентства
                self.repres_pinned = True

        elif repres and user.agency_id == repres.agency_id and repres.agency_id is not None:
            # Представитель проверяет клиента, закрепленного за агентом из этого же агентства
            self.agent_repres_pinned = True

    async def _get_unique_status(self, slug: str) -> UniqueStatus:
        """
        Получаем статус закрепления по slug
        """
        status: UniqueStatus = await self.unique_status_repo.retrieve(filters=dict(slug=slug))
        if not status:
            raise UniqueStatusNotFoundError
        return status

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

    async def _send_admin_email(self, recipients: list[str], data: dict[str, Any]) -> asyncio.Task:
        """
        Отправляем письмо администратору о результатах проверки
        """
        email_notification_template = await self.get_email_template_service(
            mail_event_slug=self.admin_email_slug,
            context=data,
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

    async def _get_admin_recipients(self, check: Check) -> Optional[list[str]]:
        """
        Получаем список получателей письма администраторов
        По умолчанию получатели - администраторы, которые привязаны к городу клиента
        Получаем город клиента из сделки, по которой прошла проверка.
        """
        if not check.amocrm_id:
            # Может не быть amocrm_id, если клиент уникальный и за ним нет сделок. Тогда письмо не отправляем
            return
        booking: Booking = await self.booking_repo.retrieve(
            filters=dict(amocrm_id=check.amocrm_id, active=True),
            prefetch_fields=["project__city"],
        )
        client_city: City = booking.project.city if booking and booking.project else None
        if not client_city:
            # Если у сделки нет проекта, то как найти город клиента?
            return

        admins: list[User] = await self.user_repo.list(
            filters=dict(receive_admin_emails=True, users_cities__in=[client_city]),
        )

        recipients: list[str] = []
        for admin in admins:
            if admin.email:
                recipients.append(admin.email)

        return recipients
