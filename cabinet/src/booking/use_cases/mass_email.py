from asyncio import Task
from typing import Type, Any

from ..decorators import logged_action
from ..entities import BaseBookingCase
from ..exceptions import BookingUserInactiveError
from ..mixins import BookingLogMixin
from ..repos import BookingRepo, Booking
from ..types import BookingEmail
from ..loggers.wrappers import booking_changes_logger
from src.notifications.services import GetEmailTemplateService


class MassEmailCase(BaseBookingCase, BookingLogMixin):
    """
    Массовая отправка писем брони
    """
    mail_event_slug: str = "success_booking"

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
        self.get_email_template_service: GetEmailTemplateService = get_email_template_service
        self.booking_email_logger = booking_changes_logger(self.booking_repo.update, self, content="Успешная "
                                                                                                  "оплата |EMAIL")

    async def __call__(self, user_id: int) -> list[Booking]:
        filters: dict[str, Any] = dict(user_id=user_id, active=True, price_payed=True, email_sent=False)
        bookings: list[Booking] = await self.booking_repo.list(
            filters=filters, related_fields=["user", "project", "property", "building", "floor"]
        )
        if bookings:
            booking: Booking = bookings[0]
            if not booking.user.is_active:
                raise BookingUserInactiveError
        data: dict[str, Any] = dict(email_sent=True)
        for booking in bookings:
            await self._send_email(booking=booking)
            await self.booking_email_logger(booking=booking, data=data)
        return bookings

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
