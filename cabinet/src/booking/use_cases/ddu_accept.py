from asyncio import Task
from datetime import datetime, timedelta
from typing import Type

from common.amocrm import AmoCRM
from common.amocrm.constants import AmoElementTypes, AmoTaskTypes
from pytz import UTC
from src.booking.loggers.wrappers import booking_changes_logger

from ..constants import OnlinePurchaseStatuses, OnlinePurchaseSteps
from ..entities import BaseBookingCase
from ..exceptions import BookingNotFoundError, BookingWrongStepError
from ..repos import Booking, BookingRepo, DDURepo
from ..services import HistoryService, NotificationService
from ..types import BookingEmail, BookingSms


class DDUAcceptCase(BaseBookingCase):
    """
    Подписание ДДУ
    """

    email_template: str = "src/booking/templates/ddu_accepted.html"
    _notification_template = "src/booking/templates/notifications/ddu_accept.json"
    _history_template = "src/booking/templates/history/ddu_accept.txt"

    remainder_task_text = "клиент согласовал договор - связаться с клиентом"

    def __init__(
        self,
        booking_repo: Type[BookingRepo],
        ddu_repo: Type[DDURepo],
        amocrm_class: Type[AmoCRM],
        sms_class: Type[BookingSms],
        email_class: Type[BookingEmail],
        history_service: HistoryService,
        notification_service: NotificationService,
    ) -> None:
        self.booking_repo: BookingRepo = booking_repo()
        self.ddu_repo: DDURepo = ddu_repo()
        self.amocrm_class: Type[AmoCRM] = amocrm_class
        self.sms_class: Type[BookingSms] = sms_class
        self.email_class: Type[BookingEmail] = email_class

        self._history_service = history_service
        self._notification_service = notification_service
        self.booking_update = booking_changes_logger(
            self.booking_repo.update, self, content="Подписание ДДУ",
        )

    async def __call__(
        self,
        *,
        booking_id: int,
        user_id: int,
    ) -> Booking:
        booking: Booking = await self.booking_repo.retrieve(
            filters=dict(active=True, id=booking_id, user_id=user_id),
            related_fields=["project", "property", "floor", "building", "ddu", "agent", "user"],
            prefetch_fields=["ddu__participants"],
        )
        if not booking:
            raise BookingNotFoundError

        previous_online_purchase_step = booking.online_purchase_step()
        self._check_requirements(booking)

        update_data = dict(
            amocrm_purchase_status=OnlinePurchaseStatuses.DDU_ACCEPTED,
            ddu_accepted=True,
            ddu_acceptance_datetime=datetime.now(tz=UTC),
        )
        booking = await self.booking_update(booking=booking, data=update_data)
        await self._notify_client(
            booking, previous_online_purchase_step=previous_online_purchase_step
        )
        await self._amocrm_hook(booking)

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
        email_options = dict(
            topic="Покупка квартиры.",
            template=self.email_template,
            context=dict(booking=booking),
            recipients=[booking.user.email],
        )
        email_service = self.email_class(**email_options)
        return email_service.as_task()

    def _send_sms(self, booking: Booking) -> Task:
        """СМС уведомление"""
        message = (
            "Покупка квартиры.\n\n"
            "Договор по покупке подтверждён и ожидает регистрации. "
            "Необходимо открыть эскроу счёт.\n\n"
            "Подробности в личном кабинете:\n"
            "www.strana.com/login"
        )
        sms_options = dict(phone=booking.user.phone, message=message)
        sms_service = self.sms_class(**sms_options)
        return sms_service.as_task()

    async def _amocrm_hook(self, booking: Booking) -> None:
        """amocrm hook"""
        amocrm: AmoCRM
        async with await self.amocrm_class() as amocrm:
            # Поменять значение поля "статус онлайн-покупки" на "согласовал договор"
            # Заполнить поле "дата и время согласования договора"
            await amocrm.update_lead(
                lead_id=booking.amocrm_id,
                online_purchase_status=booking.amocrm_purchase_status,
                ddu_acceptance_datetime=int(booking.ddu_acceptance_datetime.timestamp()),
            )

            # TODO: убрать, когда будет синхронизация ответственных у бронирований
            amocrm_lead = await amocrm.fetch_lead(lead_id=booking.amocrm_id)
            if amocrm_lead:

                # Поставить дополнительную задачу-уведомление
                # "клиент согласовал договор - связаться с клиентом" ответственному по сделке
                complete_till_datetime = booking.ddu_acceptance_datetime + timedelta(days=1)

                await amocrm.create_task(
                    entity_id=booking.amocrm_id,
                    responsible_user_id=amocrm_lead.responsible_user_id,
                    entity_type=AmoElementTypes.LEAD,
                    text=self.remainder_task_text,
                    task_type=AmoTaskTypes.CALL,
                    complete_till=int(complete_till_datetime.timestamp()),
                )

    @classmethod
    def _check_requirements(cls, booking: Booking) -> None:
        """Проверка на выполнение условий."""
        if booking.online_purchase_step() != OnlinePurchaseSteps.DDU_ACCEPT:
            raise BookingWrongStepError
