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


class DDUUploadCase(BaseBookingCase):
    """
    Загрузка ДДУ юристом
    """

    email_template: str = "src/booking/templates/ddu_uploaded.html"
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

    def _send_email(self, booking: Booking) -> Task:
        """Уведомление по почте"""
        email_options: dict[str, Any] = dict(
            topic="Покупка квартиры.",
            template=self.email_template,
            context=dict(booking=booking),
            recipients=[booking.user.email],
        )
        email_service: Any = self.email_class(**email_options)
        return email_service.as_task()

    def _send_sms(self, booking: Booking) -> Task:
        """СМС уведомление"""
        message = (
            "Покупка квартиры.\n\n"
            "Договор долевого участия составлен, войдите в личный кабинет для согласования.\n\n"
            "Подробности в личном кабинете:\n"
            "www.strana.com/login"
        )
        sms_options: dict[str, Any] = dict(phone=booking.user.phone, message=message)
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
