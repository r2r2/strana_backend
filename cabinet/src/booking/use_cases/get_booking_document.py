from src.documents.repos import DocumentRepo, Document
from src.documents.exceptions import DocumentNotFoundError
from ..entities import BaseBookingCase
from ..exceptions import BookingProjectMissingError, BookingPropertyMissingError, BookingNotFoundError
from ..repos import BookingRepo, Booking


class GetBookingDocumentCase(BaseBookingCase):
    """
    Получение документа для сделки
    """

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
        if not booking:
            raise BookingNotFoundError

        if not booking.project:
            raise BookingProjectMissingError

        if not booking.property:
            raise BookingPropertyMissingError

        document: Document = await self.document_repo.retrieve(filters=dict(slug=booking.project.city.slug))
        if not document:
            raise DocumentNotFoundError

        document_info_data: dict = dict(
            address=booking.building.address,
            price=booking.building.booking_price,
            period=booking.building.booking_period,
            premise=booking.property.premise.label,
        )
        document.text = document.text.format(**document_info_data)
        return document
