from secrets import compare_digest
from typing import Any, Type

from ..constants import OnlinePurchaseSteps
from ..entities import BaseBookingCase
from ..exceptions import BookingNotFoundError, BookingWrongStepError
from ..repos import Booking, BookingRepo


class DDUUploadRetrieveCase(BaseBookingCase):
    """
    Данные для внешней формы загрузки ДДУ юристом
    """

    def __init__(self, booking_repo: Type[BookingRepo]) -> None:
        self.booking_repo: BookingRepo = booking_repo()

    async def __call__(self, *, booking_id: int, secret: str) -> Booking:
        filters: dict[str, Any] = dict(active=True, id=booking_id)
        booking: Booking = await self.booking_repo.retrieve(
            filters=filters, prefetch_fields=["user"]
        )
        if not booking:
            raise BookingNotFoundError

        self._check_step_requirements(booking)
        self._validate_data(booking, secret)

        return booking

    @classmethod
    def _validate_data(cls, booking: Booking, secret: str) -> None:
        if booking.ddu_upload_url_secret is None or booking.ddu_upload_url_secret == "":
            raise BookingWrongStepError

        if not compare_digest(booking.ddu_upload_url_secret, secret):
            raise BookingWrongStepError

    @classmethod
    def _check_step_requirements(cls, booking: Booking) -> None:
        """Проверка на выполнение условий."""
        # Юрист может залить ДДУ, когда клиент его может изменять,
        # а также, пока клиент его не согласовал
        if booking.online_purchase_step() not in {
            OnlinePurchaseSteps.AMOCRM_DDU_UPLOADING_BY_LAWYER,
            OnlinePurchaseSteps.DDU_ACCEPT,
        }:
            raise BookingWrongStepError
