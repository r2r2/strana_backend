from typing import Any, Type, Optional

from ..constants import OnlinePurchaseSteps
from ..entities import BaseBookingCase
from ..exceptions import (
    BookingNotFoundError,
    BookingPurchaseHelpTextNotFound,
    BookingWrongStepError,
)
from ..repos import Booking, BookingRepo, PurchaseHelpText, PurchaseHelpTextRepo


class PurchaseHelpTextCase(BaseBookingCase):
    """
    Страничка "Как купить онлайн?".

    Текст отличается в зависимости от типа покупки и стадии сделки.

    Если текста с указанным типом покупки и стадией не найдено,
    достанется только тот, у которого default=True.
    """

    def __init__(
        self,
        booking_repo: Type[BookingRepo],
        purchase_help_text_repo: Type[PurchaseHelpTextRepo],
    ) -> None:
        self.booking_repo: BookingRepo = booking_repo()
        self.purchase_help_text_repo: PurchaseHelpTextRepo = purchase_help_text_repo()

    async def __call__(self, booking_id: int, user_id: int) -> PurchaseHelpText:
        filters: dict[str, Any] = dict(active=True, id=booking_id, user_id=user_id)
        booking: Optional[Booking] = await self.booking_repo.retrieve(filters=filters)

        if not booking:
            raise BookingNotFoundError

        self._check_step_requirements(booking)

        filters = dict(
            booking_online_purchase_step=booking.online_purchase_step(),
            payment_method=booking.payment_method,  # todo: payment_method
            maternal_capital=booking.maternal_capital,
            certificate=booking.housing_certificate,
            loan=booking.government_loan,
        )
        # Пытаемся достать конкретный текст
        help_text: Optional[PurchaseHelpText] = await self.purchase_help_text_repo.retrieve(
            filters=filters
        )
        if help_text is not None:
            return help_text

        help_text = await self.purchase_help_text_repo.retrieve(filters=dict(default=True))
        if help_text is None:
            raise BookingPurchaseHelpTextNotFound

        return help_text

    @classmethod
    def _check_step_requirements(cls, booking: Booking) -> None:
        """Проверка текущего шага."""
        online_purchase_step = booking.online_purchase_step()
        if not online_purchase_step:
            raise BookingWrongStepError

        if online_purchase_step in {
            OnlinePurchaseSteps.ONLINE_PURCHASE_START,
            OnlinePurchaseSteps.PAYMENT_METHOD_SELECT,
            OnlinePurchaseSteps.AMOCRM_AGENT_DATA_VALIDATION,
        }:
            raise BookingWrongStepError
