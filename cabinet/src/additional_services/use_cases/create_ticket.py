from asyncio import Task

from common.email import EmailService
from common.settings.repos import AddServiceSettingsRepo
from src.notifications.services import GetEmailTemplateService
from ..entities import BaseAdditionalServiceCase
from ..repos import (
    AdditionalServiceTicketRepo as TicketRepo,
    AdditionalServiceTicket as Ticket,
    AdditionalServiceGroupStatusRepo as GroupStatusRepo,
    AdditionalServiceGroupStatus as GroupStatus,
)
from ..models import CreateTicketRequest


class CreateTicketCase(BaseAdditionalServiceCase):
    """
    Кейс создания заявки
    """

    ticket_sent_group_status_slug: str = "ticket_sent"
    add_service_notification_slug: str = "add_service_notification"

    def __init__(
        self,
        ticket_repo: type[TicketRepo],
        group_status_repo: type[GroupStatusRepo],
        add_service_settings_repo: type[AddServiceSettingsRepo],
        email_class: type[EmailService],
        get_email_template_service: GetEmailTemplateService,
    ) -> None:
        self.ticket_repo: TicketRepo = ticket_repo()
        self.group_status_repo: GroupStatusRepo = group_status_repo()
        self.add_service_settings_repo: AddServiceSettingsRepo = (
            add_service_settings_repo()
        )
        self.email_class: type[EmailService] = email_class
        self.get_email_template_service: GetEmailTemplateService = (
            get_email_template_service
        )

    async def __call__(self, user_id: int, payload: CreateTicketRequest) -> Ticket:
        ticket_data: dict = payload.dict(exclude_none=True)
        if booking_id := ticket_data.get("booking_id"):
            # todo будет реализовано в следующей итерации
            pass
        group_status: GroupStatus = await self.group_status_repo.retrieve(
            filters=dict(slug=self.ticket_sent_group_status_slug)
        )
        ticket_data.update(user_id=user_id, group_status_id=group_status.id)
        created_ticket: Ticket = await self.ticket_repo.create(data=ticket_data)
        if created_ticket:
            await created_ticket.fetch_related("service")
            await self.send_email_notify(ticket=created_ticket)
        return created_ticket

    async def send_email_notify(self, ticket: Ticket) -> Task:
        """
        Уведомление о создании заявки
        """
        email_notification_template = await self.get_email_template_service(
            mail_event_slug=self.add_service_notification_slug,
            context=dict(
                full_name=ticket.full_name,
                phone=ticket.phone,
                service_title=ticket.service.title,
            ),
        )
        if email_notification_template and email_notification_template.is_active:
            email_options: dict = dict(
                topic=email_notification_template.template_topic,
                content=email_notification_template.content,
                lk_type=email_notification_template.lk_type.value,
                mail_event_slug=email_notification_template.mail_event_slug,
                recipients=await self.add_service_settings_repo.list().values_list(
                    "email", flat=True
                ),
            )
            email_service: EmailService = self.email_class(**email_options)
            return email_service.as_task()
