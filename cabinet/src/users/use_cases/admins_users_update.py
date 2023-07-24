import asyncio
from typing import Any, Optional, Type, Union
from enum import IntEnum

from common.email import EmailService
from src.booking.loggers.wrappers import booking_changes_logger
from src.users import services as user_services

from ..constants import UserType
from ..entities import BaseUserCase
from ..exceptions import (UserNoAgencyError,
                          UserNoAgentError, UserNotFoundError)
from ..loggers.wrappers import user_changes_logger
from ..models import RequestAdminsUsersUpdateModel
from ..repos import CheckRepo, User, UserRepo
from ..types import (UserAgency, UserAgencyRepo, UserAgentRepo, UserBooking,
                     UserBookingRepo)
from src.agents.types import AgentEmail
from src.notifications.services import GetEmailTemplateService


class LeadStatuses(IntEnum):
    """
     Статусы закрытых сделок в амо.
    """
    REALIZED: int = 142  # Успешно реализовано
    UNREALIZED: int = 143  # Закрыто и не реализовано


class AdminsUsersUpdateCase(BaseUserCase):
    """
    Изменение пользователя администратором
    """
    mail_event_slug = "assign_client"
    previous_agent_email_slug = "previous_agent_email"

    def __init__(
        self,
        user_repo: Type[UserRepo],
        check_repo: Type[CheckRepo],
        agent_repo: Type[UserAgentRepo],
        agency_repo: Type[UserAgencyRepo],
        booking_repo: Type[UserBookingRepo],
        email_class: Type[AgentEmail],
        get_email_template_service: GetEmailTemplateService,
        change_agent_service: user_services.ChangeAgentService,
    ) -> None:
        self.user_repo: UserRepo = user_repo()
        self.user_update = user_changes_logger(
            self.user_repo.update, self, content="Изменение пользователя администратором"
        )
        self.check_repo: CheckRepo = check_repo()
        self.agent_repo: UserAgentRepo = agent_repo()
        self.agency_repo: UserAgencyRepo = agency_repo()
        self.booking_repo: UserBookingRepo = booking_repo()
        self.change_agent_service: user_services.ChangeAgentService = change_agent_service
        self.email_class: Type[AgentEmail] = email_class
        self.get_email_template_service: GetEmailTemplateService = get_email_template_service

        self.booking_update = booking_changes_logger(
            self.booking_repo.update, self, content="Изменение пользователя",
        )

    async def __call__(self, user_id: int, payload: RequestAdminsUsersUpdateModel) -> User:
        u_data: dict[str, Any] = payload.dict()
        agent_id: Union[int, None] = u_data.get("agent_id", None)
        agency_id: Union[int, None] = u_data.get("agency_id", None)
        filters: dict[str, Any] = dict(id=user_id, type=UserType.CLIENT)
        user: User = await self.user_repo.retrieve(filters=filters, related_fields=["agent"])
        if not user:
            raise UserNotFoundError

        agent: Optional[User] = None
        agency: Optional[UserAgency] = None
        if agent_id:
            filters: dict[str, Any] = dict(
                id=agent_id, is_deleted=False, is_active=True, is_approved=True, type=UserType.AGENT
            )
            agent: User = await self.agent_repo.retrieve(filters=filters)
            if not agent:
                raise UserNoAgentError
        if agency_id:
            filters: dict[str, Any] = dict(id=agency_id, is_deleted=False, is_approved=True)
            agency: UserAgency = await self.agency_repo.retrieve(filters=filters)
            if not agency:
                raise UserNoAgencyError
        if agent and agency and agent.agency_id != agency.id:
            raise UserNoAgencyError

        if agent and not agency:
            bound_data: dict[str, Any] = dict(agent_id=agent.id, agency_id=agent.agency_id)
        elif agent and agency:
            bound_data: dict[str, Any] = dict(agent_id=agent.id, agency_id=agency.id)
        else:
            bound_data: dict[str, Any] = {}

        if bound_data:
            filters: dict[str, Any] = dict(
                user_id=user.id, agent_id=user.agent_id, agency_id=user.agency_id
            )
            bookings: list[UserBooking] = await self.booking_repo.list(filters=filters).exclude(
                amocrm_status_id=LeadStatuses.REALIZED,
            ).exclude(
                amocrm_status_id=LeadStatuses.UNREALIZED,
            )

            for booking in bookings:
                await self.booking_update(booking=booking, data=bound_data)

        if u_data.get("agent_id") and not u_data.get("agency_id"):
            u_data["agency_id"] = agent.agency_id

        if user.agent_id and agent:
            await self._send_email(
                recipients=[user.agent.email],
                agent_name=user.agent.full_name,
                slug=self.previous_agent_email_slug,
            )

        user: User = await self.user_update(user=user, data=u_data)

        if agent:
            self.change_agent_service.as_task(user_id=user_id, agent_id=agent.id)
        return user

    async def _send_email(self, recipients: list[str], slug, **context) -> asyncio.Task:
        """
        Отправляем письмо клиенту.
        @param recipients: list[str]
        @param context: Any (Контекст, который будет использоваться в шаблоне письма)
        @return: Task
        """
        email_notification_template = await self.get_email_template_service(
            mail_event_slug=slug,
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
