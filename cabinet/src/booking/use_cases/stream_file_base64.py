from base64 import b64encode
from typing import Any, Type, Generator

from botocore.exceptions import DataNotFoundError

from ..constants import OnlinePurchaseSteps
from ..entities import BaseBookingCase
from ..exceptions import BookingBadRequestError, BookingNotFoundError
from ..repos import Booking, BookingRepo
from ..types import BookingFileClient


class StreamFileBase64Case(BaseBookingCase):
    """
    Стриминг файла, закодированного в base64.
    """

    def __init__(
        self,
        booking_repo: Type[BookingRepo],
        file_client: BookingFileClient,
    ) -> None:
        self.booking_repo: BookingRepo = booking_repo()
        self.file_client: BookingFileClient = file_client()

    async def __call__(
        self, *, booking_id: int, user_id: int, category: str
    ) -> Generator[bytes, None, None]:
        filters: dict[str, Any] = dict(active=True, id=booking_id, user_id=user_id)
        booking: Booking = await self.booking_repo.retrieve(filters=filters)
        if not booking:
            raise BookingNotFoundError

        try:
            # Ставлю chunk_size=None, т.к. были проблемы с поломаным base64, даже если ставить
            # chunk_size как произведение 3. Проблема остаётся с тем, что сервер полностью
            # выкачивает себе файл, а потом его кодирует
            stream = self.file_client(booking.files, category, -1, chunk_size=None)
        except ValueError as err:
            raise BookingBadRequestError(str(err))

        return (b64encode(chunk) async for chunk in stream)
