import asyncio
from typing import Any, Type
from enum import IntEnum

from common.email import EmailService
from src.booking.loggers.wrappers import booking_changes_logger
from src.users import services as user_services

from ..entities import BaseUserCase
from ..exceptions import UserNoAgentError, UserNotFoundError
from ..loggers.wrappers import user_changes_logger
from ..models import RequestRepresesUsersReboundModel
from src.users.repos import User, UserRepo
from ..types import UserAgentRepo, UserBooking, UserBookingRepo
from src.notifications.services import GetEmailTemplateService


class LeadStatuses(IntEnum):
    """
     Статусы закрытых сделок в амо.
    """
    REALIZED: int = 142  # Успешно реализовано
    UNREALIZED: int = 143  # Закрыто и не реализовано


class RepresesUsersReboundCase(BaseUserCase):
    """
    Перепривязка пользователя представителем агентства
    """
    previous_agent_email_slug = "previous_agent_email"

    def __init__(
        self,
        user_repo: Type[UserRepo],
        agent_repo: Type[UserAgentRepo],
        booking_repo: Type[UserBookingRepo],
        email_class: Type[EmailService],
        get_email_template_service: GetEmailTemplateService,
        change_agent_service: user_services.ChangeAgentService,
    ) -> None:
        self.user_repo: UserRepo = user_repo()
        self.agent_repo: UserAgentRepo = agent_repo()
        self.booking_repo: UserBookingRepo = booking_repo()
        self.change_agent_service: user_services.ChangeAgentService = change_agent_service
        self.get_email_template_service: GetEmailTemplateService = get_email_template_service
        self.email_class: Type[EmailService] = email_class

        self.user_reassign = user_changes_logger(
            self.user_repo.update, self, content="Перепривязка пользователя к представителю агентства"
        )
        self.booking_update = booking_changes_logger(
            self.booking_repo.update, self, content="Подписание ДДУ",
        )

    async def __call__(
        self, user_id: int, agency_id: int, payload: RequestRepresesUsersReboundModel
    ) -> None:
        data: dict[str, Any] = payload.dict()
        to_agent_id: int = data["to_agent_id"]
        from_agent_id: int = data["from_agent_id"]
        filters: dict[str, Any] = dict(id=to_agent_id, agency_id=agency_id, is_deleted=False)
        to_agent: User = await self.agent_repo.retrieve(filters=filters)
        filters: dict[str, Any] = dict(id=from_agent_id, agency_id=agency_id, is_deleted=False)
        from_agent: User = await self.agent_repo.retrieve(filters=filters)
        if not to_agent or not from_agent:
            raise UserNoAgentError
        filters: dict[str, Any] = dict(id=user_id, agent_id=from_agent.id)
        user: User = await self.user_repo.retrieve(filters=filters)
        if not user:
            raise UserNotFoundError

        if from_agent != to_agent:
            # Именно смене агентов, т.е. когда 1 агент меняется на другого.
            await self._send_email(
                recipients=[from_agent.email],
                agent_name=from_agent.full_name,
                client_name=user.full_name,
                slug=self.previous_agent_email_slug,
            )

        data: dict[str, Any] = dict(agent_id=to_agent.id)
        user: User = await self.user_reassign(user=user, data=data)

        filters: dict[str, Any] = dict(user_id=user.id, agent_id=from_agent.id, agency_id=agency_id)
        bookings: list[UserBooking] = await self.booking_repo.list(filters=filters).exclude(
            amocrm_status_id=LeadStatuses.REALIZED,
        ).exclude(
            amocrm_status_id=LeadStatuses.UNREALIZED,
        )

        for booking in bookings:
            data: dict[str, Any] = dict(
                agent_id=to_agent.id,
                agency_id=agency_id,
            )
            await self.booking_update(booking=booking, data=data)
        self.change_agent_service.as_task(user_id=user_id, agent_id=to_agent_id)

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
