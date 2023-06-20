import base64
from datetime import datetime, timedelta
from typing import Any, Callable, Type, Union

from uuid import uuid4
import sentry_sdk
from pytz import UTC

from ...properties.constants import PropertyStatuses
from ..constants import (PAYMENT_PROPERTY_NAME, BookingStages,
                         BookingSubstages, PaymentStatuses, PaymentView)
from ..decorators import logged_action
from ..entities import BaseBookingCase
from ..exceptions import (BookingNotFoundError, BookingOnlinePaymentError,
                          BookingTimeOutError, BookingWrongStepError)
from ..loggers.wrappers import booking_changes_logger
from ..mixins import BookingLogMixin
from ..models import RequestCheckParamsModel
from ..repos import Booking, BookingRepo
from ..types import BookingSberbank


class CheckParamsCase(BaseBookingCase, BookingLogMixin):
    """
    Проверка параметров бронирования
    """

    def __init__(
        self,
        create_booking_log_task: Any,
        booking_repo: Type[BookingRepo],
        sberbank_class: Type[BookingSberbank],
        global_id_decoder: Callable[[str], tuple[str, Union[str, int]]],
    ) -> None:
        self.booking_repo: BookingRepo = booking_repo()

        self.create_booking_log_task: Any = create_booking_log_task
        self.sberbank_class: Type[BookingSberbank] = sberbank_class
        self.global_id_decoder: Callable[[str], tuple[str, Union[str, int]]] = global_id_decoder
        self.booking_update = booking_changes_logger(
            self.booking_repo.update, self, content="Проверка параметров бронирования",
        )
        self.booking_check_logger = booking_changes_logger(self.booking_repo.update, self, content="Проверка "
                                                                                                   "параметров")
        self.booking_fail_logger = booking_changes_logger(self.booking_repo.update, self, content="Ошибка получения "
                                                                                                  "ссылки")
        self.booking_success_logger = booking_changes_logger(self.booking_repo.update, self, content="Успешное "
                                                                                                     "получение "
                                                                                                     "ссылки")

    async def __call__(
        self, user_id: int, booking_id: int, payload: RequestCheckParamsModel
    ) -> Booking:

        step_data: dict[str, Any] = payload.dict()

        filters: dict[str, Any] = dict(active=True, id=booking_id, user_id=user_id)
        booking: Booking = await self.booking_repo.retrieve(
            filters=filters, related_fields=["user", "project", "project__city", "property", "building"]
        )

        profitbase_id = base64.b64decode(booking.property.global_id).decode("utf-8").split(":")[-1]
        sentry_sdk.set_context(
            "booking",
            {
                "active": booking.active,
                "amocrm_id": booking.amocrm_id,
                "contract_accepted": booking.contract_accepted,
                "personal_filled": booking.personal_filled,
                "params_checked": booking.params_checked,
                "price_payed": booking.price_payed,
                "expires": booking.expires,
            },
        )
        sentry_sdk.set_context(
            "property",
            {
                "status": PropertyStatuses.to_label(booking.property.status),
                "profitbase_id": profitbase_id,
                "building_name": booking.building.name,
                "project_name": booking.project.name,
            },
        )

        if not booking:
            sentry_sdk.capture_message("cabinet/CheckParamsCase: Бронирование не найдено")
            raise BookingNotFoundError
        if not booking.step_two():
            sentry_sdk.capture_message(
                "cabinet/CheckParamsCase: BookingWrongStepError: Персональные данные не заполнены"
            )
            raise BookingWrongStepError
        if not booking.time_valid():
            sentry_sdk.capture_message("cabinet/CheckParamsCase: Таймер бронирования истёк")
            raise BookingTimeOutError

        data: dict[str, Any] = dict(
            payment_page_view=PaymentView(value=step_data.pop("payment_page_view")),
            payment_order_number=uuid4(),
        )
        booking: Booking = await self.booking_update(booking=booking, data=data)

        payment: Union[dict[str, Any], str] = await self._online_payment(booking=booking)

        if not payment.get("formUrl", None):
            data: dict[str, Any] = dict(
                params_checked=False,
                amocrm_stage=BookingStages.BOOKING,
                payment_status=PaymentStatuses.FAILED,
                amocrm_substage=BookingSubstages.BOOKING,
            )
            await self.booking_fail_logger(booking=booking, data=data)
            sentry_sdk.capture_message(
                "cabinet/CheckParamsCase: BookingOnlinePaymentError: "
                "Не удалось сгенерировать ссылку для оплаты"
            )
            raise BookingOnlinePaymentError

        payment_id: str = payment.get("orderId")
        payment_url: str = payment.get("formUrl")

        data: dict[str, Any] = dict(
            payment_id=payment_id, payment_url=payment_url, payment_status=PaymentStatuses.PENDING
        )
        booking: Booking = await self.booking_success_logger(booking=booking, data=data)

        data: dict[str, Any] = step_data
        booking: Booking = await self.booking_check_logger(booking=booking, data=data)

        filters: dict[str, Any] = dict(active=True, id=booking.id, user_id=user_id)
        booking: Booking = await self.booking_repo.retrieve(
            filters=filters,
            related_fields=["project", "project__city", "property", "floor", "building", "ddu", "agent", "agency"],
            prefetch_fields=["ddu__participants"],
        )
        return booking

    # @logged_action(content="ПОЛУЧЕНИЕ ССЫЛКИ | SBERBANK")
    async def _online_payment(self, booking: Booking) -> Union[dict[str, Any], str]:
        """online payment"""
        payment_options: dict[str, Any] = dict(
            city=booking.project.city.slug,
            user_email=booking.user.email,
            user_phone=booking.user.phone,
            booking_order_id=booking.payment_id,
            booking_price=int(booking.payment_amount),
            user_full_name=booking.user.full_name,
            page_view=booking.payment_page_view.value,
            booking_currency=booking.payment_currency,
            booking_order_number=booking.payment_order_number.hex,
            property_name=PAYMENT_PROPERTY_NAME.format(booking.property.article),
            property_id=self.global_id_decoder(booking.property.global_id)[1],
            timeout=(booking.expires - datetime.now(tz=UTC) - timedelta(seconds=10)).seconds,
        )
        sberbank_service: BookingSberbank = self.sberbank_class(**payment_options)
        payment: Union[dict[str, Any], str] = await sberbank_service("pay")
        return payment
