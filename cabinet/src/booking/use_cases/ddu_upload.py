from asyncio import Task
from secrets import compare_digest
from typing import Any, Type

from ..constants import BookingFileType, OnlinePurchaseSteps, UploadPath
from ..entities import BaseBookingCase
from ..exceptions import (BookingBadRequestError, BookingNotFoundError,
                          BookingWrongStepError)
from ..loggers.wrappers import booking_changes_logger
from ..repos import Booking, BookingRepo
from ..services import HistoryService, NotificationService
from ..types import BookingEmail, BookingFileProcessor, BookingSms
from src.notifications.services import GetSmsTemplateService, GetEmailTemplateService


class DDUUploadCase(BaseBookingCase):
    """
    Загрузка ДДУ юристом
    """

    sms_event_slug = "booking_ddu_uploaded"
    mail_event_slug: str = "booking_ddu_uploaded"
    _notification_template = "src/booking/templates/notifications/ddu_upload.json"
    _history_template = "src/booking/templates/history/ddu_upload.txt"

    def __init__(
        self,
        booking_repo: Type[BookingRepo],
        file_processor: BookingFileProcessor,
        sms_class: Type[BookingSms],
        email_class: Type[BookingEmail],
        history_service: HistoryService,
        notification_service: NotificationService,
        get_sms_template_service: GetSmsTemplateService,
        get_email_template_service: GetEmailTemplateService,
    ) -> None:
        self.booking_repo: BookingRepo = booking_repo()
        self.file_processor: BookingFileProcessor = file_processor
        self.sms_class: Type[BookingSms] = sms_class
        self.email_class: Type[BookingEmail] = email_class

        self._history_service = history_service
        self._notification_service = notification_service
        self.booking_update = booking_changes_logger(
            self.booking_repo.update, self, content="Загрузка ДДУ юристом",
        )
        self.get_sms_template_service: GetSmsTemplateService = get_sms_template_service
        self.get_email_template_service: GetEmailTemplateService = get_email_template_service

    async def __call__(self, *, booking_id: int, secret: str, ddu_file: Any) -> Booking:
        filters: dict[str, Any] = dict(active=True, id=booking_id)
        booking: Booking = await self.booking_repo.retrieve(
            filters=filters, related_fields=["user"]
        )
        if not booking:
            raise BookingNotFoundError

        previous_online_purchase_step = booking.online_purchase_step()
        self._check_step_requirements(booking=booking)
        self._validate_data(booking=booking, secret=secret)

        booking_data = dict(amocrm_ddu_uploaded_by_lawyer=True)
        booking_data["files"] = await self.file_processor(
            files={BookingFileType.DDU_BY_LAWYER: [ddu_file]},
            path=UploadPath.BOOKING_FILES,
            choice_class=BookingFileType,
            container=getattr(booking, "files", None),
            filter_by_hash=False,
        )

        booking = await self.booking_update(booking=booking, data=booking_data)
        await self._notify_client(
            booking, previous_online_purchase_step=previous_online_purchase_step
        )

        await self._history_service.execute(
            booking=booking,
            previous_online_purchase_step=previous_online_purchase_step,
            template=self._history_template,
        )

        return booking

    async def _notify_client(self, booking: Booking, previous_online_purchase_step: str) -> None:
        """Уведомление клиента о том, что ДДУ готов для согласования."""
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

    @classmethod
    def _validate_data(cls, *, booking: Booking, secret: str) -> None:
        """Проверка на выполнение условий."""
        if booking.ddu_upload_url_secret is None or booking.ddu_upload_url_secret == "":
            raise BookingBadRequestError("У бронирования нет ссылки на загрузку ДДУ")
        if not compare_digest(booking.ddu_upload_url_secret, secret):
            raise BookingBadRequestError("Указанная ссылка загрузки ДДУ не была найдена.")

    @classmethod
    def _check_step_requirements(cls, *, booking: Booking) -> None:
        """Проверка на выполнение условий."""
        # Юрист может залить ДДУ, когда клиент его может изменять,
        # а также, пока клиент его не согласовал
        if booking.online_purchase_step() not in {
            OnlinePurchaseSteps.AMOCRM_DDU_UPLOADING_BY_LAWYER,
            OnlinePurchaseSteps.DDU_ACCEPT,
        }:
            raise BookingWrongStepError
