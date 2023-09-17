from common.settings.repos import BookingSettings, BookingSettingsRepo
from src.booking.exceptions import BookingSourceNotFoundError
from src.properties.repos import Property
from src.booking.repos import BookingReservationMatrix, BookingReservationMatrixRepo, BookingSource, BookingSourceRepo


async def get_booking_reserv_time(created_source: str, booking_property: Property) -> float:
    """
    Получение времени бронирования для сделки (ч)
    Используется в: BindBookingPropertyCase, AcceptContractCase, FastBookingWebhookCase, CreateBookingCase
    """
    await booking_property.fetch_related("project")
    booking_reserv: BookingReservationMatrix = await BookingReservationMatrixRepo().retrieve(
        filters=dict(created_source=created_source),
        prefetch_fields=["project"],
    )

    if booking_property.project in booking_reserv.project:
        booking_reserv_time: float = booking_reserv.reservation_time
    else:
        booking_settings: BookingSettings = await BookingSettingsRepo().list().first()
        booking_reserv_time: float = booking_settings.default_flats_reserv_time

    return booking_reserv_time


async def get_booking_source(slug: str) -> BookingSource:
    """
    Получение источника бронирования
    """
    booking_source: BookingSource = await BookingSourceRepo().retrieve(
        filters=dict(slug=slug)
    )
    if not booking_source:
        raise BookingSourceNotFoundError
    return booking_source
