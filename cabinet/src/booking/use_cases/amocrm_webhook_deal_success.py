from asyncio import Task
from typing import Any, Callable, Type
from urllib.parse import unquote

import structlog

from ..constants import OnlinePurchaseSteps
from ..entities import BaseBookingCase
from ..exceptions import BookingNotFoundError, BookingWrongStepError
from ..mixins import BookingLogMixin
from ..repos import Booking, BookingRepo, WebhookRequestRepo
from ..services import HistoryService, NotificationService
from ..types import BookingEmail, BookingSms
from ..loggers.wrappers import booking_changes_logger
from src.notifications.services import GetSmsTemplateService, GetEmailTemplateService

logger = structlog.getLogger('amocrm_deal_success_hook')


class AmoCRMWebhookDealSuccessCase(BaseBookingCase, BookingLogMixin):
    """
    Вебхук АМО. Договор был подписан и сделка состоялась.

    Также оповещаем клиента об этом.
    """

    sms_event_slug = "booking_deal_success"
    mail_event_slug = "amocrm_signed"
    _notification_template = "src/booking/templates/notifications/amocrm_webhook_deal_success.json"
    _history_template = "src/booking/templates/history/amocrm_webhook_deal_success.txt"

    def __init__(
        self,
        create_booking_log_task: Any,
        booking_repo: Type[BookingRepo],
        webhook_request_repo: Type[WebhookRequestRepo],
        sms_class: Type[BookingSms],
        email_class: Type[BookingEmail],
        history_service: HistoryService,
        notification_service: NotificationService,
        get_sms_template_service: GetSmsTemplateService,
        get_email_template_service: GetEmailTemplateService,
    ) -> None:
        self.booking_repo: BookingRepo = booking_repo()
        self.webhook_request_repo: WebhookRequestRepo = webhook_request_repo()
        self.create_booking_log_task: Any = create_booking_log_task

        self.sms_class: Type[BookingSms] = sms_class

        self._history_service = history_service
        self.email_class: Type[BookingEmail] = email_class
        self._notification_service = notification_service
        self.booking_update = booking_changes_logger(self.booking_repo.update, self, content="Договор был подписан")
        self.get_sms_template_service: GetSmsTemplateService = get_sms_template_service
        self.get_email_template_service: GetEmailTemplateService = get_email_template_service

    async def __call__(self, payload: bytes) -> Booking:
        payload_decoded = unquote(payload.decode("utf-8"))
        logger.info('Requested amo hook', raw_data=payload_decoded)

        # Сохраняем тело запроса
        webhook_request_data = dict(category="deal_success", body=payload_decoded)
        await self.webhook_request_repo.create(webhook_request_data)

        booking_amocrm_id, deal_success = self._parse_data(payload_decoded)
        logger.info('Data parsed', booking_amocrm_id=booking_amocrm_id, deal_success=deal_success)
        booking = await self.booking_repo.retrieve(
            filters=dict(amocrm_id=booking_amocrm_id), related_fields=["user"]
        )
        if booking is None:
            logger.warning('Booking not found', amocrm_id=booking_amocrm_id)
            raise BookingNotFoundError

        previous_online_purchase_step = booking.online_purchase_step()
        self._validate_requirements(booking)

        data = dict(amocrm_signed=deal_success)
        booking: Booking = await self.booking_update(booking=booking, data=data)
        if deal_success:
            await self._notify_client(
                booking, previous_online_purchase_step=previous_online_purchase_step
            )

            await self._history_service.execute(
                booking=booking,
                previous_online_purchase_step=previous_online_purchase_step,
                template=self._history_template,
            )
        logger.info('Success', amocrm_signed=deal_success)

        return booking

    @staticmethod
    def _parse_data(request_body: str) -> tuple[int, bool]:
        """parse data"""
        items = request_body.split("&")
        dictionary: dict[str, str] = {}
        for item in items:
            try:
                key, value = item.split("=")
            except ValueError:
                continue
            dictionary[key] = value

        booking_amocrm_id = int(dictionary["ID"])
        deal_success = dictionary["deal-success"].lower() == "да"
        return booking_amocrm_id, deal_success

    def _validate_requirements(self, booking: Booking) -> None:
        """validate_requirements"""
        if booking.online_purchase_step() != OnlinePurchaseSteps.AMOCRM_SIGNING:
            logger.warning('Wrong step',
                           step=booking.online_purchase_step(),
                           required=OnlinePurchaseSteps.AMOCRM_SIGNING)
            raise BookingWrongStepError

    async def _notify_client(self, booking: Booking, previous_online_purchase_step: str) -> None:
        """Уведомление клиента о том, что сделка состоялась."""
        await self._send_sms(booking)
        await self._send_email(booking)
        await self._notification_service(
            booking=booking,
            previous_online_purchase_step=previous_online_purchase_step,
            template=self._notification_template,
        )

    async def _send_email(self, booking: Booking) -> Task:
        """Уведомление по почте"""
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

    async def _send_sms(self, booking: Booking) -> Task:
        """СМС уведомление"""
        sms_notification_template = await self.get_sms_template_service(
            sms_event_slug=self.sms_event_slug,
        )
        if sms_notification_template and sms_notification_template.is_active:
            sms_options: dict[str, Any] = dict(
                phone=booking.user.phone,
                message=sms_notification_template.template_text,
                lk_type=sms_notification_template.lk_type.value,
                sms_event_slug=sms_notification_template.sms_event_slug,
            )
            sms_service: Any = self.sms_class(**sms_options)
            return sms_service.as_task()
