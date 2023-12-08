from typing import Any

from common.numbers import number_to_text
from common.sentry.utils import send_sentry_log
from src.documents.repos import DocumentRepo, Document
from src.documents.exceptions import DocumentNotFoundError
from ..entities import BaseBookingCase
from ..exceptions import BookingProjectMissingError, BookingPropertyMissingError, BookingNotFoundError
from ..repos import BookingRepo, Booking


class GetBookingDocumentCase(BaseBookingCase):
    """
    Получение документа для сделки
    """
    price_units = (("рубль", "рубля", "рублей"), "m")
    period_units = (("календарный день", "календарных дня", "календарных дней"), "m")

    def __init__(
        self,
        document_repo: type[DocumentRepo],
        booking_repo: type[BookingRepo],
    ) -> None:
        self.document_repo: DocumentRepo = document_repo()
        self.booking_repo: BookingRepo = booking_repo()

    async def __call__(self, booking_id: int, user_id: int) -> Document:
        booking_filters: dict = dict(active=True, id=booking_id, user_id=user_id)
        booking: Booking = await self.booking_repo.retrieve(
            filters=booking_filters,
            related_fields=["project__city", "property__property_type", "building"]
        )
        try:
            self._check_booking_valid(booking=booking)
        except (BookingNotFoundError, BookingProjectMissingError, BookingPropertyMissingError) as ex:
            sentry_ctx: dict[str, Any] = dict(
                booking_id=booking_id,
                user_id=user_id,
                booking_filters=booking_filters,
                ex=ex,
            )
            await send_sentry_log(
                tag="GetBookingDocumentCase",
                message="Booking not found",
                context=sentry_ctx,
            )
            raise ex

        document: Document = await self.document_repo.retrieve(filters=dict(slug=booking.project.city.slug))
        if not document:
            sentry_ctx: dict[str, Any] = {
                "booking_id": booking_id,
                "user_id": user_id,
                "booking.project.city.slug": booking.project.city.slug,
                "ex": DocumentNotFoundError,
            }
            await send_sentry_log(
                tag="GetBookingDocumentCase",
                message="Document not found",
                context=sentry_ctx,
            )
            raise DocumentNotFoundError

        price: int = booking.payment_amount if booking.payment_amount else booking.building.booking_price
        document_info_data: dict = dict(
            address=booking.building.address,
            price=self._get_price_text(price),
            period=self._get_period_text(booking.building.booking_period),
            premise=booking.property.premise.label,
        )
        document.text = document.text.format(**document_info_data)
        return document

    def _check_booking_valid(self, booking: Booking) -> None:
        if not booking:
            raise BookingNotFoundError

        if not booking.project:
            raise BookingProjectMissingError

        if not booking.property:
            raise BookingPropertyMissingError

    @classmethod
    def _get_price_text(cls, price: int) -> str:
        price_as_text = number_to_text(price, cls.price_units).capitalize()
        price_unit = price_as_text.rsplit(" ", 1)[-1]

        # 5000.00 рублей (Пять тысяч рублей ноль копеек)
        return "{price} {price_unit} ({price_as_text} ноль копеек)".format(
            price=price, price_unit=price_unit, price_as_text=price_as_text
        )

    @classmethod
    def _get_period_text(cls, period: int) -> str:
        period_as_text_with_units = number_to_text(period, cls.period_units).capitalize()
        period_as_text_without_units = number_to_text(period).capitalize()

        period_unit: str | None = None
        for _period_unit in cls.period_units[0]:
            if _period_unit in period_as_text_with_units:
                period_unit = _period_unit
                break

        # 20 (Двадцать) календарных дней
        return "{period} ({period_as_text}) {period_unit}".format(
            period=period, period_as_text=period_as_text_without_units, period_unit=period_unit
        )
