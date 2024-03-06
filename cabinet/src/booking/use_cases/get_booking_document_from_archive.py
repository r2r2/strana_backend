from typing import Any, NamedTuple

from src.booking.exceptions import BookingNotFoundError, BookingSignedOfferNotFoundError
from src.booking.repos import BookingEventHistoryRepo, BookingRepo, DocumentArchiveRepo

from common.numbers import number_to_text
from src.users.exceptions import UserNotFoundError


class BookingInfo(NamedTuple):
    booking_id: int
    period: int | None
    address: str | None
    premise: str | None
    price: int | None


class GetDocumentFromArchiveCase:
    """
    Получить заполненный документ оферты из архива документов.
    """

    price_units = (("рубль", "рубля", "рублей"), "m")
    period_units = (("календарный день", "календарных дня", "календарных дней"), "m")

    def __init__(
            self,
            document_archive_repo: DocumentArchiveRepo,
            booking_event_history_repo: BookingEventHistoryRepo,
            booking_repo: BookingRepo
    ) -> None:
        self.document_archive_repo: DocumentArchiveRepo = document_archive_repo
        self.booking_event_history_repo: BookingEventHistoryRepo = booking_event_history_repo
        self.booking_repo: BookingRepo = booking_repo

    async def __call__(self, booking_id: int, booking_event_history_id: int, user_id: int | None) -> dict[str, str]:
        booking_info: BookingInfo = await self.get_booking_info(booking_id, user_id)
        signed_offer_text: str = await self.get_signed_offer_text(
            booking_info.booking_id,
            booking_event_history_id
        )
        formatted_document_from_archive: str = signed_offer_text.format(
            address=booking_info.address,
            premise=booking_info.premise,
            price=self._get_price_text(booking_info.price),
            period=self._get_period_text(booking_info.period),
        )
        return {"signed_offer": formatted_document_from_archive}

    async def get_booking_info(self, booking_id: int, user_id: int | None) -> BookingInfo:
        """
        Получаем данные из сделки, нужные для подстановки в оферту.
        """
        if user_id is None:
            raise UserNotFoundError

        booking_data = (
            await self.booking_repo.retrieve(filters={"id": booking_id, "user_id": user_id})
            .values(
                booking_id="id",
                period="booking_period",
                address="building__address",
                premise="property__property_type__label",
                price="payment_amount"
            )
        )
        if not booking_data:
            raise BookingNotFoundError

        return BookingInfo(**booking_data)

    async def get_signed_offer_text(self, booking_id: int, booking_event_history_id: int) -> str:
        """
        Получаем текст(шаблон) оферты из архива оферт, с которой соглашался клиент.
        """
        signed_offer_text = (
            await self.booking_event_history_repo.retrieve(
                filters={"booking_id": booking_id, "id": booking_event_history_id}
            )
            .values(offer_text="signed_offer__offer_text")
        )
        if not signed_offer_text or not signed_offer_text.get("offer_text"):
            raise BookingSignedOfferNotFoundError

        return signed_offer_text["offer_text"]

    @classmethod
    def _get_price_text(cls, price: int | None) -> str:
        if price is None:
            return ""

        kopecks: str = str(price).split(".")[-1]
        if kopecks == "00":
            kopecks = "ноль"
        else:
            kopecks = " ".join(number_to_text(int(kopecks), cls.price_units).split()[:-1])

        price_as_text = number_to_text(price, cls.price_units).capitalize()
        price_unit = price_as_text.rsplit(" ", 1)[-1]

        return "{price} {price_unit} ({price_as_text} {kopecks} копеек)".format(
            price=price, price_unit=price_unit, price_as_text=price_as_text, kopecks=kopecks
        )

    @classmethod
    def _get_period_text(cls, period: int | None) -> str:
        if period is None:
            return ""
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
