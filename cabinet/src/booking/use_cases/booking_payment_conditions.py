from datetime import datetime, timedelta
from pytz import UTC

from src.buildings.repos import BuildingBookingTypeRepo, BuildingBookingType as BookingType
from ..entities import BaseBookingCase
from ..exceptions import BookingNotFoundError, BookingTypeMissingError
from ..models import RequestBookingPaymentConditionsModel
from ..repos import BookingRepo, Booking


class BookingPaymentConditionsCase(BaseBookingCase):
    """
    Кейс выбора условий оплаты
    """
    def __init__(
        self,
        booking_repo: type[BookingRepo],
        building_booking_type_repo: type[BuildingBookingTypeRepo],
    ) -> None:
        self.booking_repo: BookingRepo = booking_repo()
        self.building_booking_type_repo: BuildingBookingTypeRepo = building_booking_type_repo()

    async def __call__(self, booking_id: int, payload: RequestBookingPaymentConditionsModel) -> Booking:
        booking: Booking = await self.booking_repo.retrieve(filters=dict(id=booking_id))
        if not booking:
            raise BookingNotFoundError
        booking_type: BookingType = await self.building_booking_type_repo.retrieve(
            filters=dict(id=payload.booking_type_id)
        )
        if not booking_type:
            raise BookingTypeMissingError
        booking_payment_conditions_data: dict = dict(
            booking_period=booking_type.period,
            payment_amount=booking_type.price,
            until=datetime.now(tz=UTC) + timedelta(days=booking_type.period),
            condition_chosen=True,
        )
        return await self.booking_repo.update(model=booking, data=booking_payment_conditions_data)
