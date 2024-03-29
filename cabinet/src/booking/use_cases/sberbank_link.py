import base64
from datetime import datetime, timedelta
from typing import Any, Callable, Type, Union

from uuid import uuid4
import sentry_sdk
from pytz import UTC

from common.sentry.utils import send_sentry_log
from common.unleash.client import UnleashClient
from config import sberbank_config
from config.feature_flags import FeatureFlags
from ...properties.constants import PropertyStatuses
from ..constants import (PAYMENT_PROPERTY_NAME, BookingStages,
                         BookingSubstages, PaymentStatuses, PaymentView)
from ..decorators import logged_action
from ..entities import BaseBookingCase
from ..exceptions import (BookingNotFoundError, BookingOnlinePaymentError,
                          BookingTimeOutError, BookingWrongStepError)
from ..loggers.wrappers import booking_changes_logger
from ..mixins import BookingLogMixin
from ..models import RequestSberbankLinkModel
from ..repos import Booking, BookingRepo, AcquiringRepo
from ..types import BookingSberbank


class SberbankLinkCase(BaseBookingCase, BookingLogMixin):
    """
    Получение ссылки сбербанка
    """

    def __init__(
        self,
        create_booking_log_task: Any,
        booking_repo: Type[BookingRepo],
        acquiring_repo: type[AcquiringRepo],
        sberbank_class: Type[BookingSberbank],
        global_id_decoder: Callable[..., tuple[str, Union[int, str]]],
    ) -> None:
        self.booking_repo: BookingRepo = booking_repo()
        self.acquiring_repo: AcquiringRepo = acquiring_repo()
        self.sberbank_class: Type[BookingSberbank] = sberbank_class
        self.create_booking_log_task: Any = create_booking_log_task
        self.global_id_decoder: Callable[..., tuple[str, Union[int, str]]] = global_id_decoder
        self.booking_update = booking_changes_logger(
            self.booking_repo.update, self, content="Получение ссылки сбербанка | EMAIL",
        )
        self.booking_fail_logger = booking_changes_logger(self.booking_repo.update, self, content="Повторная ссылка, "
                                                                                                  "ошибка| SBERBANK")
        self.booking_success_logger = booking_changes_logger(self.booking_repo.update, self, content="Повторная "
                                                                                                     "ссылка,"
                                                                                                     "успех| SBERBANK")

    async def __call__(
        self, booking_id: int, user_id: int, payload: RequestSberbankLinkModel
    ) -> Booking:
        step_data: dict[str, Any] = payload.dict()

        filters: dict[str, Any] = dict(id=booking_id, user_id=user_id, active=True)
        booking: Booking = await self.booking_repo.retrieve(
            filters=filters, related_fields=["user", "project", "project__city", "property", "building"]
        )

        if not booking:
            sentry_ctx: dict[str, Any] = dict(
                booking_id=booking_id,
                user_id=user_id,
                booking_filters=filters,
                ex=BookingNotFoundError,
                payload=payload,
            )
            await send_sentry_log(
                tag="SberbankLinkCase",
                message="Бронирование не найдено",
                context=sentry_ctx,
            )
            raise BookingNotFoundError

        profitbase_id = base64.b64decode(booking.property.global_id).decode("utf-8").split(":")[-1]
        sentry_ctx: dict[str, Any] = {
            "booking": {
                "active": booking.active,
                "amocrm_id": booking.amocrm_id,
                "contract_accepted": booking.contract_accepted,
                "personal_filled": booking.personal_filled,
                "params_checked": booking.params_checked,
                "price_payed": booking.price_payed,
                "expires": booking.expires,
            },
            "property": {
                "status": PropertyStatuses.to_label(booking.property.status),
                "profitbase_id": profitbase_id,
                "building_name": booking.building.name,
                "project_name": booking.project.name,
            },
        }

        if not booking.step_three():
            sentry_ctx.update({"ex": BookingWrongStepError})
            await send_sentry_log(
                tag="SberbankLinkCase",
                message="Параметры бронирования не подтверждены",
                context=sentry_ctx,
            )
            raise BookingWrongStepError
        if booking.step_four():
            sentry_ctx.update({"ex": BookingWrongStepError})
            await send_sentry_log(
                tag="SberbankLinkCase",
                message="Бронирование уже оплачено",
                context=sentry_ctx,
            )
            raise BookingWrongStepError
        if not booking.time_valid():
            sentry_ctx.update({"ex": BookingTimeOutError})
            await send_sentry_log(
                tag="SberbankLinkCase",
                message="Бронирование истекло",
                context=sentry_ctx,
            )
            raise BookingTimeOutError

        data: dict[str, Any] = dict(
            payment_page_view=PaymentView(value=step_data.pop("payment_page_view")),
            payment_order_number=uuid4(),
        )
        booking: Booking = await self.booking_update(booking=booking, data=data)

        payment: Union[dict[str, Any], str] = await self._online_payment(booking=booking)

        if not payment.get("formUrl", None):
            extra_data: dict[str, Any] = dict(
                payment_status=PaymentStatuses.FAILED,
                amocrm_stage=BookingStages.BOOKING,
                amocrm_substage=BookingSubstages.BOOKING,
            )
            data.update(extra_data)
            await self.booking_fail_logger(booking=booking, data=data)
            sentry_ctx.update(
                {
                    "ex": BookingOnlinePaymentError,
                    "payment": payment,
                }
            )
            await send_sentry_log(
                tag="SberbankLinkCase",
                message="Не удалось сгенерировать ссылку для оплаты",
                context=sentry_ctx,
            )
            raise BookingOnlinePaymentError

        payment_id: str = payment.get("orderId")
        payment_url: str = payment.get("formUrl")

        extra_data: dict[str, Any] = dict(
            payment_id=payment_id, payment_url=payment_url, payment_status=PaymentStatuses.PENDING
        )
        data.update(extra_data)
        booking: Booking = await self.booking_success_logger(booking=booking, data=data)

        return booking

    # @logged_action(content="ПОВТОРНОЕ ПОЛУЧЕНИЕ ССЫЛКИ | SBERBANK")
    async def _online_payment(self, booking: Booking) -> Union[dict[str, Any], str]:
        """online payment"""
        if UnleashClient().is_enabled(FeatureFlags.strana_lk_2090):
            filters = dict(is_active=True, city=booking.project.city)
            acquiring = await self.acquiring_repo.retrieve(filters=filters)
            if acquiring is not None:
                _username: str | None = acquiring.username
                _password: str | None = acquiring.password
            else:
                _username = _password = None
        else:
            _username: str | None = sberbank_config.get(f"{booking.project.city.slug}_username")
            _password: str | None = sberbank_config.get(f"{booking.project.city.slug}_password")

        payment_options: dict[str, Any] = dict(
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
            username=_username,
            password=_password,
            amocrm_id=booking.amocrm_id,
        )
        sberbank_service: BookingSberbank = self.sberbank_class(**payment_options)
        payment: Union[dict[str, Any], str] = await sberbank_service("pay")
        return payment


class SberbankLinkCaseV2(BaseBookingCase, BookingLogMixin):
    """
    Получение ссылки сбербанка
    """

    def __init__(
        self,
        create_booking_log_task: Any,
        booking_repo: Type[BookingRepo],
        acquiring_repo: type[AcquiringRepo],
        sberbank_class: Type[BookingSberbank],
        global_id_decoder: Callable[..., tuple[str, Union[int, str]]],
    ) -> None:
        self.booking_repo: BookingRepo = booking_repo()
        self.acquiring_repo: AcquiringRepo = acquiring_repo()
        self.sberbank_class: Type[BookingSberbank] = sberbank_class
        self.create_booking_log_task: Any = create_booking_log_task
        self.global_id_decoder: Callable[..., tuple[str, Union[int, str]]] = global_id_decoder
        self.booking_update = booking_changes_logger(
            self.booking_repo.update, self, content="Получение ссылки сбербанка | EMAIL",
        )
        self.booking_fail_logger = booking_changes_logger(self.booking_repo.update, self, content="Повторная ссылка, "
                                                                                                  "ошибка| SBERBANK")
        self.booking_success_logger = booking_changes_logger(self.booking_repo.update, self, content="Повторная "
                                                                                                     "ссылка,"
                                                                                                     "успех| SBERBANK")

    async def __call__(
        self, booking_id: int, user_id: int, payload: RequestSberbankLinkModel
    ) -> Booking:
        step_data: dict[str, Any] = payload.dict()

        filters: dict[str, Any] = dict(id=booking_id, user_id=user_id, active=True)
        booking: Booking = await self.booking_repo.retrieve(
            filters=filters, related_fields=["user", "project", "project__city", "property", "building"]
        )
        await self.validate_booking(booking=booking)

        data: dict[str, Any] = dict(
            payment_page_view=PaymentView(value=step_data.pop("payment_page_view")),
            payment_order_number=uuid4(),
        )
        booking: Booking = await self.booking_update(booking=booking, data=data)

        payment: dict[str, Any] = await self.process_payment(booking=booking, data=data)
        data.update(
            dict(
                payment_id=payment.get("orderId"),
                payment_url=payment.get("formUrl"),
                payment_status=PaymentStatuses.PENDING,
            )
        )
        booking: Booking = await self.booking_success_logger(booking=booking, data=data)

        return booking

    async def process_payment(self, booking: Booking, data: dict[str, Any]) -> dict[str, Any]:
        """process payment"""
        payment: dict[str, Any] | str = await self._online_payment(booking=booking)

        if not isinstance(payment, dict):
            raise ValueError(f"cabinet/SberbankLinkCase: payment is not dict {payment=} {type(payment)=}")

        if not payment.get("formUrl", None):
            data.update(
                dict(
                    payment_status=PaymentStatuses.FAILED,
                    amocrm_stage=BookingStages.BOOKING,
                    amocrm_substage=BookingSubstages.BOOKING,
                )
            )
            await self.booking_fail_logger(booking=booking, data=data)
            sentry_sdk.capture_message(
                "cabinet/SberbankLinkCase: BookingOnlinePaymentError: "
                "Не удалось сгенерировать ссылку для оплаты"
            )
            raise BookingOnlinePaymentError
        return payment

    async def _online_payment(self, booking: Booking) -> Union[dict[str, Any], str]:
        """online payment"""
        if UnleashClient().is_enabled(FeatureFlags.strana_lk_2090):
            filters = dict(is_active=True, city=booking.project.city)
            acquiring = await self.acquiring_repo.retrieve(filters=filters)
            if acquiring is not None:
                _username: str | None = acquiring.username
                _password: str | None = acquiring.password
            else:
                _username = _password = None
        else:
            _username: str | None = sberbank_config.get(f"{booking.project.city.slug}_username")
            _password: str | None = sberbank_config.get(f"{booking.project.city.slug}_password")

        payment_options: dict[str, Any] = dict(
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
            username=_username,
            password=_password,
        )
        sberbank_service: BookingSberbank = self.sberbank_class(**payment_options)
        payment: Union[dict[str, Any], str] = await sberbank_service("pay")
        return payment

    async def validate_booking(self, booking: Booking) -> None:
        if not booking:
            sentry_sdk.capture_message(
                "cabinet/SberbankLinkCase: BookingNotFoundError: Бронирование не найдено"
            )
            raise BookingNotFoundError

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

        if not booking.step_three():
            sentry_sdk.capture_message(
                "cabinet/SberbankLinkCase: BookingWrongStepError: "
                "Параметры бронирования не подтверждены"
            )
            raise BookingWrongStepError
        if booking.step_four():
            sentry_sdk.capture_message(
                "cabinet/SberbankLinkCase: BookingWrongStepError: Бронирование уже оплачено"
            )
            raise BookingWrongStepError
        if not booking.time_valid():
            sentry_sdk.capture_message(
                "cabinet/SberbankLinkCase: BookingTimeOutError: Бронирование истекло"
            )
            raise BookingTimeOutError
