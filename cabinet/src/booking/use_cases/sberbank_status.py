"""
Sberbank status UseCase
"""
import asyncio
from asyncio import Task
from datetime import datetime, timedelta
from secrets import compare_digest
from typing import Any, Callable, Literal, Type, Union, Awaitable

from pytz import UTC

from ..constants import (PAYMENT_PROPERTY_NAME, BookingSubstages,
                         PaymentStatuses)
from ..decorators import logged_action
from ..entities import BaseBookingCase
from ..exceptions import BookingNotFoundError, BookingRedirectFailError
from ..loggers.wrappers import booking_changes_logger
from ..mixins import BookingLogMixin
from ..repos import Booking, BookingRepo
from ..services import HistoryService, ImportBookingsService
from ..types import BookingAmoCRM, BookingEmail, BookingSberbank, BookingSms
from ...task_management.constants import PaidBookingSlug
from ...task_management.services import UpdateTaskInstanceStatusService
from src.notifications.services import GetSmsTemplateService, GetEmailTemplateService


class SberbankStatusCase(BaseBookingCase, BookingLogMixin):
    """
    Статус оплаты сбербанка
    """

    sms_event_slug = "booking_sberbank_status"
    mail_event_slug: str = "success_booking"
    agent_mail_event_slug: str = "success_booking_agent_notification"
    _history_template = "src/booking/templates/history/sberbank_status_succeeded.txt"

    def __init__(
        self,
        sms_class: Type[BookingSms],
        site_config: dict[str, Any],
        create_amocrm_log_task: Any,
        create_booking_log_task: Any,
        update_task_instance_status_service: UpdateTaskInstanceStatusService,
        booking_config: dict[str, Any],
        sberbank_config: dict[str, Any],
        email_class: Type[BookingEmail],
        booking_repo: Type[BookingRepo],
        amocrm_class: Type[BookingAmoCRM],
        sberbank_class: Type[BookingSberbank],
        global_id_decoder: Callable[[str], tuple[str, Union[str, int]]],
        history_service: HistoryService,
        import_bookings_service: ImportBookingsService,
        get_sms_template_service: GetSmsTemplateService,
        get_email_template_service: GetEmailTemplateService,
    ) -> None:
        self.booking_repo: BookingRepo = booking_repo()

        self.sms_class: Type[BookingSms] = sms_class
        self.email_class: Type[BookingEmail] = email_class
        self.amocrm_class: Type[BookingAmoCRM] = amocrm_class
        self.create_amocrm_log_task: Any = create_amocrm_log_task
        self.sberbank_class: Type[BookingSberbank] = sberbank_class
        self.create_booking_log_task: Any = create_booking_log_task
        self.update_task_instance_status_service: UpdateTaskInstanceStatusService = update_task_instance_status_service
        self.global_id_decoder: Callable[[str], tuple[str, Union[str, int]]] = global_id_decoder

        self.secret: str = sberbank_config["secret"]
        self.site_host: str = site_config["site_host"]
        self.site_email: str = site_config["site_email"]
        self.frontend_return_url: str = sberbank_config["frontend_return_url"]
        self.frontend_fast_return_url: str = sberbank_config["frontend_fast_return_url"]
        self.additional_time_minutes: int = booking_config["additional_time_minutes"]

        self._history_service = history_service
        self.import_bookings_service = import_bookings_service
        self.booking_success_logger = booking_changes_logger(self.booking_repo.update, self, content="Успешная ОПЛАТА "
                                                                                                     "| SBERBANK")
        self.booking_fail_logger = booking_changes_logger(self.booking_repo.update, self, content="Неуспешная | "
                                                                                                  "SBERBANK")
        self.get_sms_template_service: GetSmsTemplateService = get_sms_template_service
        self.get_email_template_service: GetEmailTemplateService = get_email_template_service

    async def __call__(self, kind: Literal["success", "fail"], secret: str, payment_id: str, *args, **kwargs) -> str:
        filters: dict[str, Any] = dict(payment_id=payment_id, active=True)
        booking: Booking = await self.booking_repo.retrieve(
            filters=filters,
            related_fields=[
                "user", "agent", "project", "project__city", "property", "building", "floor",
            ]
        )

        if not booking:
            raise BookingNotFoundError
        if not compare_digest(secret, self.secret):
            raise BookingRedirectFailError

        if booking.user:
            await self.import_bookings_service(user_id=booking.user.id)

        status: dict[str, Any] = await self._check_status(booking=booking)
        payment_status: Union[int, None] = status.get("orderStatus", PaymentStatuses.FAILED)
        data: dict[str, Any] = dict(payment_status=payment_status)

        if payment_status == PaymentStatuses.SUCCEEDED:
            tags: list[str] = booking.tags if booking.tags else []
            tags.append("Бронь оплачена")
            data.update(
                tags=tags,
                email_sent=True,
                price_payed=True,
                params_checked=True,
                should_be_deactivated_by_timer=False,
            )
            note_data: dict[str, Any] = dict(
                element="lead",
                lead_id=booking.amocrm_id,
                note="common",
                text="Успешная оплата онлайн бронирования",
            )
            self.create_amocrm_log_task.delay(note_data=note_data)

            async_tasks: list[Awaitable] = [
                self.update_task_instance_status(booking_id=booking.id, status_slug=PaidBookingSlug.SUCCESS.value),
                self._send_sms(booking=booking),
                self._send_email(booking=booking),
            ]
            if booking.is_agent_assigned():
                async_tasks.append(self._send_agent_email(booking=booking))
            await asyncio.gather(*async_tasks)
            await self._amocrm_processing(booking=booking, payment_status=True)
        else:
            data.update(params_checked=False)
            await self.booking_fail_logger(booking=booking, data=data)
            note_data: dict[str, Any] = dict(
                element="lead",
                lead_id=booking.amocrm_id,
                note="common",
                text="Неуспешная оплата онлайн бронирования",
            )
            self.create_amocrm_log_task.delay(note_data=note_data)
            data["expires"]: datetime = booking.expires + timedelta(
                minutes=self.additional_time_minutes
            )

        await self.booking_success_logger(booking=booking, data=data)
        if payment_status == PaymentStatuses.SUCCEEDED:
            await self._history_service.execute(
                booking=booking,
                previous_online_purchase_step=booking.online_purchase_step(),
                template=self._history_template,
                params={"until": booking.until.strftime("%d.%m.%Y")},
            )

        url: str = f"{booking.origin}{self.frontend_return_url}/{booking.id}/4/?status={kind}"
        if booking.is_fast_booking():
            url: str = f"{booking.origin}{self.frontend_fast_return_url}/{booking.id}/3/?status={kind}"
        return url

    # @logged_action(content="ПОЛУЧЕНИЕ СТАТУСА | SBERBANK")
    async def _check_status(self, booking: Booking) -> dict[str, Any]:
        """
        Docs
        """
        status_options: dict[str, Any] = dict(
            city=booking.project.city.slug,
            user_email=booking.user.email,
            user_phone=booking.user.phone,
            user_full_name=booking.user.full_name,
            property_id=self.global_id_decoder(booking.property.global_id)[1],
            property_name=PAYMENT_PROPERTY_NAME.format(booking.property.article),
            booking_currency=booking.payment_currency,
            booking_price=int(booking.payment_amount),
            booking_order_id=booking.payment_id,
            booking_order_number=booking.payment_order_number.hex,
            page_view=booking.payment_page_view,
        )
        sberbank_service: Any = self.sberbank_class(**status_options)
        status: Union[dict[str, Any], str] = await sberbank_service("status")
        return status

    # @logged_action(content="ОПЛАЧЕНО | AMOCRM")
    async def _amocrm_processing(self, booking: Booking, payment_status: bool) -> int:
        """
        Обновление сделки в amoCRM
        """
        if booking.amocrm_substage in (
            BookingSubstages.MORTGAGE_DONE,
            BookingSubstages.MORTGAGE_LEAD,
            BookingSubstages.MORTGAGE_FILED,
        ):
            # Не меняем статус, если это ипотека
            status = booking.amocrm_substage
        else:
            status = BookingSubstages.PAID_BOOKING if payment_status else BookingSubstages.BOOKING

        booking_period = booking.booking_period or 0
        booking_until_datetime = datetime.now(tz=UTC) + timedelta(days=booking_period)
        async with await self.amocrm_class() as amocrm:
            lead_options: dict[str, Any] = dict(
                status=status,
                lead_id=booking.amocrm_id,
                city_slug=booking.project.city.slug,
                tags=booking.tags,
                booking_end=booking.booking_period,
                booking_price=int(booking.payment_amount),
                booking_until_datetime=int(booking_until_datetime.timestamp()),
            )
            data: list[Any] = await amocrm.update_lead(**lead_options)
            lead_id: int = data[0]["id"]
        return lead_id

    # @logged_action(content="УСПЕШНАЯ ОПЛАТА | EMAIL")
    async def _send_email(self, booking: Booking) -> Task:
        """
        Docs
        """
        email_notification_template = await self.get_email_template_service(
            mail_event_slug=self.mail_event_slug,
            context=dict(booking=booking),
        )

        if email_notification_template and email_notification_template.is_active:
            email_options: dict[str, Any] = dict(
                topic=email_notification_template.template_topic,
                content=email_notification_template.content,
                recipients=[self.site_email],
                lk_type=email_notification_template.lk_type.value,
                mail_event_slug=email_notification_template.mail_event_slug,
            )
            email_service: Any = self.email_class(**email_options)
            return email_service.as_task()

    async def _send_agent_email(self, booking: Booking) -> Task:
        """
        Уведомление агента об успешном бронировании по почте
        """
        email_notification_template = await self.get_email_template_service(
            mail_event_slug=self.agent_mail_event_slug,
            context=dict(booking=booking),
        )

        if email_notification_template and email_notification_template.is_active:
            email_options: dict[str, Any] = dict(
                topic=email_notification_template.template_topic.format(booking_id=booking.id),
                content=email_notification_template.content,
                recipients=[booking.agent.email],
                lk_type=email_notification_template.lk_type.value,
                mail_event_slug=email_notification_template.mail_event_slug,
            )
            email_service: Any = self.email_class(**email_options)
            return email_service.as_task()

    # @logged_action(content="УСПЕШНАЯ ОПЛАТА | SMS")
    async def _send_sms(self, booking: Booking) -> Task:
        """
        Docs
        """
        sms_notification_template = await self.get_sms_template_service(
            sms_event_slug=self.sms_event_slug,
        )
        if sms_notification_template and sms_notification_template.is_active:
            sms_options: dict[str, Any] = dict(
                phone=booking.user.phone,
                message=sms_notification_template.template_text.format(project_name=booking.project.name),
                lk_type=sms_notification_template.lk_type.value,
                sms_event_slug=sms_notification_template.sms_event_slug,
            )
            sms_service: Any = self.sms_class(**sms_options)
            return sms_service.as_task()

    async def update_task_instance_status(self, booking_id: int, status_slug: str) -> None:
        """
        Обновление статуса задачи
        """
        await self.update_task_instance_status_service(booking_id=booking_id, status_slug=status_slug)
