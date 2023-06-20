from typing import Any, Callable, Optional, Type
from asyncio import Task

from common.email import EmailService
from src.agents.exceptions import AgentHasNoAgencyError, AgentNotFoundError
from src.booking.loggers.wrappers import booking_changes_logger
from src.notifications.services import GetEmailTemplateService
from src.represes.exceptions import RepresNotFoundError
from src.users.loggers.wrappers import user_changes_logger
from src.users.constants import UserType

from ..entities import BaseAgencyCase
from ..types import (AgencyAgentRepo, AgencyBooking, AgencyBookingRepo,
                     AgencyRepresRepo, AgencyUser, AgencyUserRepo, AgencyEmail)


class FireAgentCase(BaseAgencyCase):
    """
    Увольнение агента.
    """

    repres_from_admin_event_slug = "admin_fire_agent"
    repres_from_agent_event_slug = "agent_fire_from_agency"
    to_agent_event_slug = "fire_agent"

    def __init__(
        self,
        user_repo: Type[AgencyUserRepo],
        agent_repo: Type[AgencyAgentRepo],
        repres_repo: Type[AgencyRepresRepo],
        booking_repo: Type[AgencyBookingRepo],
        email_class: Type[AgencyEmail],
        get_email_template_service: GetEmailTemplateService,
        fire_agent_task: Callable,
    ) -> None:
        self.user_repo: AgencyUserRepo = user_repo()
        self.agent_repo: AgencyAgentRepo = agent_repo()
        self.repres_repo: AgencyRepresRepo = repres_repo()
        self.booking_repo: AgencyBookingRepo = booking_repo()
        self.email_class: Type[AgencyEmail] = email_class
        self.get_email_template_service = get_email_template_service
        self.fire_agent_task: Any = fire_agent_task

        self.users_bulk_update: Callable = user_changes_logger(
            self.user_repo.bulk_update,
            self,
            content="Перепривязка клиентов уволенного агента за представителем агентства",
        )
        self.agent_update = user_changes_logger(
            self.agent_repo.update,
            self,
            content="Отвязка агентства от уволенного агента",
        )
        self.booking_bulk_update: Callable = booking_changes_logger(
            self.booking_repo.bulk_update,
            self,
            content="Перепривязка всех сделок уволенного агента за представителем агентства",
        )

    async def __call__(
        self,
        agent_id: int,
        role: str,
        repres_id: Optional[int] = None,
    ) -> dict[str, Any]:
        agent: AgencyUser = await self.agent_repo.retrieve(
            filters=dict(id=agent_id),
            related_fields=["agency"],
        )
        if not agent or agent.type.value != UserType.AGENT:
            raise AgentNotFoundError
        if not agent.agency:
            raise AgentHasNoAgencyError

        if not repres_id:
            repres: AgencyUser = await agent.agency.maintainer
        else:
            repres: AgencyUser = await self.repres_repo.retrieve(
                filters=dict(id=repres_id),
                related_fields=["agency"],
            )
        if not repres:
            raise RepresNotFoundError

        filters: dict[str, Any] = dict(agent_id=agent.id)
        agent_bookings: list[AgencyBooking] = await self.booking_repo.list(filters=filters)

        data: dict[str, Any] = dict(agent_id=repres.id)
        await self.users_bulk_update(filters=filters, data=data)
        await self.booking_bulk_update(filters=filters, data=data)

        # отвязываем уволенного агента от всех сделок в амо и от агентства в амо (взамен привязываем представителя)
        self.fire_agent_task.delay(
            agent_amocrm_id=agent.amocrm_id,
            repres_amocrm_id=repres.amocrm_id,
            agency_amocrm_id=agent.agency.amocrm_id,
        )

        data: dict[str, Any] = dict(agency_id=None)
        await self.agent_update(agent, data=data)

        # формируем список сделок из БД для вывода в ответе апи
        if role in (UserType.ADMIN, UserType.REPRES):
            booking_ids = [booking.id for booking in agent_bookings]
            prefetch_fields = [
                "agent",
                "agency",
                "user",
                "project",
                "project__city",
                "property",
                "property__floor",
                "amocrm_status",
            ]
            bookings = await self.booking_repo.list(
                filters=dict(id__in=booking_ids),
                prefetch_fields=prefetch_fields,
            )

            await self._send_email(
                recipients=[agent.email],
                mail_event_slug=self.to_agent_event_slug,
                agency=repres.agency,
            )

            # отправляем письмо представителю о том, что агент уволен администратором
            if role == UserType.ADMIN:
                await self._send_email(
                    recipients=[repres.email],
                    mail_event_slug=self.repres_from_admin_event_slug,
                    agency=repres.agency,
                )

            return dict(bookings=bookings)
        else:
            await self._send_email(
                recipients=[repres.email],
                mail_event_slug=self.repres_from_agent_event_slug,
                agent=agent,
            )
            return

    async def _send_email(
        self,
        recipients: list[str],
        mail_event_slug: str,
        **context,
    ) -> Task:
        email_notification_template = await self.get_email_template_service(
            mail_event_slug=mail_event_slug,
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
