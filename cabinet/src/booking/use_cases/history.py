from typing import Type

from ..entities import BaseBookingCase
from ..models.history import (
    ResponseBookingHistoryModel,
    BookingHistoryModel,
    BookingModel,
    PropertyModel,
    UserModel,
    DocumentsModel,
)
from ..repos import BookingHistoryRepo


class HistoryCase(BaseBookingCase):
    """
    История сделок конкретного пользователя
    """

    def __init__(self, booking_history_repo: Type[BookingHistoryRepo]) -> None:
        self.booking_history_repo: BookingHistoryRepo = booking_history_repo()

    async def __call__(self, user_id: int, limit: int, offset: int) -> ResponseBookingHistoryModel:
        booking_histories, next_page = await self.booking_history_repo.list(
            user_id=user_id, limit=limit, offset=offset
        )
        return ResponseBookingHistoryModel(
            next_page=next_page,
            results=[
                BookingHistoryModel(
                    id=history.id,
                    booking=BookingModel(
                        id=history.booking_id,
                        online_purchase_step=history.created_at_online_purchase_step,
                    ),
                    message=history.message,
                    property=PropertyModel.from_orm(history.property),
                    created_at=history.created_at,
                    user=UserModel.from_orm(history.user),
                    documents=(
                        [
                            [DocumentsModel.parse_obj(document) for document in document_group]
                            for document_group in history.documents
                        ]
                        if history.documents is not None
                        else []
                    ),
                )
                for history in booking_histories
            ],
        )
