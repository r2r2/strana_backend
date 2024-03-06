from src.booking.entities import BaseBookingCamelCaseModel


class ResponseBookingDocumentFromArchiveModel(BaseBookingCamelCaseModel):
    signed_offer: str
