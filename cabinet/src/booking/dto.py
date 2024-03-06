from dataclasses import dataclass

from src.booking.repos import Booking


@dataclass
class FastBookingWebhookResponseDTO:
    """
    Response from FastBookingWebhookCase
    """
    booking: Booking
    sms_text: str = ""
