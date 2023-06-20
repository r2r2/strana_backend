from asyncio import Task
from typing import Any, Type
from urllib.parse import unquote

import structlog

from common.email import EmailService
from ..constants import OnlinePurchaseSteps
from ..entities import BaseBookingCase
from ..exceptions import BookingNotFoundError, BookingWrongStepError
from ..mixins import BookingLogMixin
from ..repos import Booking, BookingRepo, WebhookRequestRepo
from ..services import HistoryService, NotificationService
from ..types import BookingEmail, BookingSms
from ..loggers.wrappers import booking_changes_logger
from src.notifications.services import GetSmsTemplateService, GetEmailTemplateService

logger = structlog.getLogger('amocrm_access_deal_hook')


class AmoCRMWebhookAccessDealCase(BaseBookingCase, BookingLogMixin):
    """
    Вебхук АМО. Данные были проверены агентом.

    Когда клиент отправляет данные для связи с банком или подаёт заявку на ипотеку на этапе выбора
    способа покупки, ему отображается экран "Подождите, введённые данные на проверке". Когда
    менеджер в AmoCRM подтвердит, вебхук придёт сюда.

    Также оповещаем клиента об этом.
    """

    sms_event_slug = "booking_access_deal"
    mail_event_slug = "amocrm_agent_data_validated"
    _notification_template = "src/booking/templates/notifications/amocrm_webhook_access_deal.json"
    _history_template = "src/booking/templates/history/amocrm_webhook_access_deal.txt"

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
        self.email_class: Type[BookingEmail] = email_class

        self._history_service = history_service
        self._notification_service = notification_service
        self.get_sms_template_service: GetSmsTemplateService = get_sms_template_service
        self.get_email_template_service: GetEmailTemplateService = get_email_template_service
        self.booking_update = booking_changes_logger(self.booking_repo.update, self, content="Данные были проверены "
                                                                                             "агентом| INTERNAL")

    async def __call__(self, payload: bytes) -> Booking:
        payload_decoded = unquote(payload.decode("utf-8"))

        # Сохраняем тело запроса
        webhook_request_data = dict(category="access_deal", body=payload_decoded)
        await self.webhook_request_repo.create(webhook_request_data)

        logger.info('Requested amo hook', request_data=webhook_request_data)

        booking_amocrm_id, access_deal = self._parse_data(payload_decoded)
        logger.info('Data parsed', booking_amocrm_id=booking_amocrm_id, access_deal=access_deal)
        booking = await self.booking_repo.retrieve(
            filters=dict(amocrm_id=booking_amocrm_id), related_fields=["user"]
        )
        if booking is None:
            logger.warning('Booking does mot found', amocrm_id=booking_amocrm_id)
            raise BookingNotFoundError

        previous_online_purchase_step = booking.online_purchase_step()
        self._validate_requirements(booking)

        data = dict(amocrm_agent_data_validated=access_deal)
        booking: Booking = await self.booking_update(booking=booking, data=data)

        if access_deal:
            await self._notify_client(booking, previous_online_purchase_step)

            await self._history_service.execute(
                booking=booking,
                previous_online_purchase_step=previous_online_purchase_step,
                template=self._history_template,
            )
        logger.info('Access deal done', amocrm_agent_data_validated=access_deal)
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
        access_deal = dictionary["access-deal"].lower() == "да"
        return booking_amocrm_id, access_deal

    def _validate_requirements(self, booking: Booking) -> None:
        """validate_requirements"""
        if booking.online_purchase_step() != OnlinePurchaseSteps.AMOCRM_AGENT_DATA_VALIDATION:
            logger.warning('Wrong booking step',
                           step=booking.online_purchase_step(),
                           required=OnlinePurchaseSteps.AMOCRM_AGENT_DATA_VALIDATION)
            raise BookingWrongStepError

    async def _notify_client(self, booking: Booking, previous_online_purchase_step: str) -> None:
        """Уведомление клиента о том, что данные были проверены."""
        await self._send_sms(booking)
        await self._send_booking_email(
            recipients=[booking.user.email],
            online_purchase_id=booking.online_purchase_id
        )
        await self._notification_service(
            booking=booking,
            previous_online_purchase_step=previous_online_purchase_step,
            template=self._notification_template,
        )

    async def _send_booking_email(self, recipients: list[str], **context) -> Task:
        """
        Уведомление о бронировании по почте
        """
        email_notification_template = await self.get_email_template_service(
            mail_event_slug=self.mail_event_slug,
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
