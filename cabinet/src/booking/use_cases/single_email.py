from asyncio import Task
from typing import Type, Any, Callable

from ..mixins import BookingLogMixin
from ..types import BookingEmail
from ..entities import BaseBookingCase
from ..repos import BookingRepo, Booking
from ..exceptions import BookingAlreadyEmailedError, BookingUserInactiveError
from ..decorators import logged_action
from ..loggers.wrappers import booking_changes_logger
from src.notifications.services import GetEmailTemplateService


class SingleEmailCase(BaseBookingCase, BookingLogMixin):
    """
    Отправка одного письма брони
    """
    mail_event_slug = "success_booking"

    def __init__(
            self,
            create_booking_log_task: Any,
            booking_repo: Type[BookingRepo],
            email_class: Type[BookingEmail],
            get_email_template_service: GetEmailTemplateService,
    ) -> None:
        self.booking_repo: BookingRepo = booking_repo()

        self.email_class: Type[BookingEmail] = email_class
        self.create_booking_log_task: Any = create_booking_log_task
        self.booking_update = booking_changes_logger(self.booking_repo.update, self, content="Успешная | EMAIL")
        self.get_email_template_service: GetEmailTemplateService = get_email_template_service

    async def __call__(self, booking_id: int, user_id: int) -> Booking:

        filters: dict[str, Any] = dict(id=booking_id, user_id=user_id, active=True, price_payed=True)
        booking: Booking = await self.booking_repo.retrieve(
            filters=filters, related_fields=["user", "project", "property", "building", "floor"]
        )
        if not booking.user.is_active:
            raise BookingUserInactiveError
        if booking.email_sent:
            raise BookingAlreadyEmailedError
        await self._send_email(booking=booking)
        data: dict[str, Any] = dict(email_sent=True)
        booking: Booking = await self.booking_update(booking=booking, data=data)
        return booking

    # @logged_action(content="УСПЕШНАЯ ОПЛАТА | EMAIL")
    async def _send_email(self, booking: Booking) -> Task:
        email_notification_template = await self.get_email_template_service(
            mail_event_slug=self.mail_event_slug,
            context=dict(booking=booking),
        )

        if email_notification_template and email_notification_template.is_active:
            email_options: dict[str, Any] = dict(
                topic=email_notification_template.template_topic,
                content=email_notification_template.content,
                recipients=[booking.user.email],
                lk_type=email_notification_template.lk_type.value,
                mail_event_slug=email_notification_template.mail_event_slug,
            )
            email_service: Any = self.email_class(**email_options)
            return email_service.as_task()
