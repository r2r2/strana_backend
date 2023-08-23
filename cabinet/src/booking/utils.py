from common.settings.repos import BookingSettings, BookingSettingsRepo
from src.properties.repos import Property
from src.booking.repos import BookingReservationMatrix, BookingReservationMatrixRepo


async def get_booking_reserv_time(created_source: str, booking_property: Property) -> float:
    """
    Получение времени бронирования для сделки (ч)
    Используется в: BindBookingPropertyCase, AcceptContractCase, FastBookingWebhookCase
    """
    booking_reserv: BookingReservationMatrix = await BookingReservationMatrixRepo().retrieve(
        filters=dict(project=booking_property.project, created_source=created_source),
    )
    if booking_reserv:
        booking_reserv_time: float = booking_reserv.reservation_time
    else:
        booking_settings: BookingSettings = await BookingSettingsRepo().retrieve(
            filters=dict(),
        )
        booking_reserv_time: float = booking_settings.default_flats_reserv_time

    return booking_reserv_time
