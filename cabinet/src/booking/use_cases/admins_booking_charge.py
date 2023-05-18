from asyncio import create_task
from datetime import datetime
from decimal import Decimal
from typing import Any, Callable, Coroutine, Type

from pytz import UTC

from ..entities import BaseBookingCase
from ..exceptions import BookingChargeReachedError, BookingNotFoundError
from ..loggers.wrappers import booking_changes_logger
from ..models import RequestAdminsBookingChargeModel
from ..repos import Booking, BookingRepo
from ..types import BookingNotificationRepo


class AdminsBookingChargeCase(BaseBookingCase):
    """
    Изменении коммиссии сделки
    """

    agent_decremented_template: str = (
        "Коммиссия по сделкам за клиента <strong>{user_display}</strong> "
        'снижена до <span class="highlight>{commission}%</span>.'
    )
    agency_decremented_template_one: str = (
        "Коммиссия по сделкам за клиента <strong>{user_display}</strong> для агента "
        '<strong>{agent_display}</strong> снижена до <span class="highlight>{commission}%</span>.'
    )
    agency_decremented_template_two: str = (
        "Коммиссия по сделкам за клиента <strong>{user_display}</strong>"
        'снижена до <span class="highlight>{commission}%</span>.'
    )

    agent_start_template: str = (
        'Установлена коммиссия <span class="highlight>{commission}%</span> '
        "по сделкам за клиента <strong>{user_display}</strong>."
    )
    agency_start_template_one: str = (
        'Установлена коммиссия <span class="highlight>{commission}%</span> '
        "по сделкам за клиента <strong>{user_display}</strong> для агента <strong>{agent_display}</strong>."
    )
    agency_start_template_two: str = (
        'Установлена коммиссия <span class="highlight>{commission}%</span> '
        "по сделкам за клиента <strong>{user_display}</strong>."
    )

    agent_normalized_template: str = (
        "Коммиссия по сделкам за клиента <strong>{user_display}</strong> "
        'возвращена в изначальное значение <span class="highlight>{commission}%</span>.'
    )
    agency_normalized_template_one: str = (
        "Коммиссия по сделкам за клиента <strong>{user_display}</strong> для агента <strong>{agent_display}</strong> "
        'возвращена в изначальное значение <span class="highlight>{commission}%</span>.'
    )
    agency_normalized_template_two: str = (
        "Коммиссия по сделкам за клиента <strong>{user_display}</strong> "
        'возвращена в изначальное значение <span class="highlight>{commission}%</span>.'
    )

    agent_incremented_template: str = (
        "Коммиссия по сделкам за клиента <strong>{user_display}</strong> "
        'повышена до <span class="highlight>{commission}%</span>.'
    )
    agency_incremented_template_one: str = (
        "Коммиссия по сделкам за клиента <strong>{user_display}</strong> для агента "
        '<strong>{agent_display}</strong> повышена до <span class="highlight>{commission}%</span>.'
    )
    agency_incremented_template_two: str = (
        "Коммиссия по сделкам за клиента <strong>{user_display}</strong> "
        'повышена до <span class="highlight>{commission}%</span>.'
    )

    def __init__(
        self, booking_repo: Type[BookingRepo], notification_repo: Type[BookingNotificationRepo]
    ) -> None:
        self.booking_repo: BookingRepo = booking_repo()
        self.notification_repo: BookingNotificationRepo = notification_repo()
        self.booking_update = booking_changes_logger(
            self.booking_repo.update, self, content="Изменении коммиссии сделки",
        )

    async def __call__(self, booking_id: int, payload: RequestAdminsBookingChargeModel) -> Booking:
        data: dict[str, Any] = payload.dict()
        commission: Decimal = data["commission"]
        filters: dict[str, Any] = dict(id=booking_id, active=True)
        booking: Booking = await self.booking_repo.retrieve(
            filters=filters, related_fields=["user", "agent", "property"]
        )
        if not booking:
            raise BookingNotFoundError
        task = None
        if booking.start_commission is not None and commission > booking.start_commission:
            raise BookingChargeReachedError
        if booking.start_commission is None:
            data["decremented"]: bool = False
            data["start_commission"]: Decimal = commission
            task: Callable[..., Coroutine] = self._create_start_notifications
        elif booking.start_commission == commission and booking.commission != commission:
            data["decremented"]: bool = False
            task: Callable[..., Coroutine] = self._create_normalize_notifications
        elif booking.commission < commission:
            data["decremented"]: bool = True
            task: Callable[..., Coroutine] = self._create_increment_notifications
        elif booking.commission > commission:
            data["decremented"]: bool = True
            task: Callable[..., Coroutine] = self._create_decrement_notifications
        if booking.property_id and booking.property.price:
            data["commission_value"]: int = int(booking.property.price * (commission / 100))
        booking: Booking = await self.booking_update(booking=booking, data=data)
        if task:
            create_task(task(booking=booking))
        return booking

    async def _create_decrement_notifications(self, booking: Booking) -> bool:
        """."""
        user_display: str = str(booking.user)
        agent_display: str = str(booking.agent) if booking.agent_id else str()
        reason_display: str = booking.decrement_reason if booking.decrement_reason else str()
        if booking.agent_id:
            message: str = self.agent_decremented_template.format(
                user_display=user_display, commission=booking.commission
            )
            if reason_display:
                message += f" Причина: {reason_display}"
            data: dict[str, Any] = dict(
                message=message, created=datetime.now(tz=UTC), user_id=booking.agent_id
            )
            await self.notification_repo.create(data=data)
        if booking.is_agency_assigned():
            if booking.is_agent_assigned():
                message: str = self.agency_decremented_template_one.format(
                    user_display=user_display,
                    agent_display=agent_display,
                    commission=booking.commission,
                )
            else:
                message: str = self.agency_decremented_template_two.format(
                    user_display=user_display, commission=booking.commission
                )
            if reason_display:
                message += f" Причина: {reason_display}"
            data: dict[str, Any] = dict(
                message=message, created=datetime.now(tz=UTC), agency_id=booking.agency_id
            )
            await self.notification_repo.create(data=data)
        return True

    async def _create_start_notifications(self, booking: Booking) -> bool:
        """."""
        user_display: str = str(booking.user)
        agent_display: str = str(booking.agent) if booking.agent_id else str()
        reason_display: str = booking.decrement_reason if booking.decrement_reason else str()
        if booking.agent_id:
            message: str = self.agent_decremented_template.format(
                user_display=user_display, commission=booking.commission
            )
            if reason_display:
                message += f" Причина: {reason_display}"
            data: dict[str, Any] = dict(
                message=message, created=datetime.now(tz=UTC), user_id=booking.agent_id
            )
            await self.notification_repo.create(data=data)
        if booking.agency_id:
            if booking.agent_id:
                message: str = self.agency_decremented_template_one.format(
                    user_display=user_display,
                    agent_display=agent_display,
                    commission=booking.commission,
                )
            else:
                message: str = self.agency_decremented_template_two.format(
                    user_display=user_display, commission=booking.commission
                )
            if reason_display:
                message += f" Причина: {reason_display}"
            data: dict[str, Any] = dict(
                message=message, created=datetime.now(tz=UTC), agency_id=booking.agency_id
            )
            await self.notification_repo.create(data=data)
        return True

    async def _create_increment_notifications(self, booking: Booking) -> bool:
        """."""
        user_display: str = str(booking.user)
        agent_display: str = str(booking.agent) if booking.agent_id else str()
        reason_display: str = booking.decrement_reason if booking.decrement_reason else str()
        if booking.agent_id:
            message: str = self.agent_decremented_template.format(
                user_display=user_display, commission=booking.commission
            )
            if reason_display:
                message += f" Причина: {reason_display}"
            data: dict[str, Any] = dict(
                message=message, created=datetime.now(tz=UTC), user_id=booking.agent_id
            )
            await self.notification_repo.create(data=data)
        if booking.agency_id:
            if booking.agent_id:
                message: str = self.agency_decremented_template_one.format(
                    user_display=user_display,
                    agent_display=agent_display,
                    commission=booking.commission,
                )
            else:
                message: str = self.agency_decremented_template_two.format(
                    user_display=user_display, commission=booking.commission
                )
            if reason_display:
                message += f" Причина: {reason_display}"
            data: dict[str, Any] = dict(
                message=message, created=datetime.now(tz=UTC), agency_id=booking.agency_id
            )
            await self.notification_repo.create(data=data)
        return True

    async def _create_normalize_notifications(self, booking: Booking) -> bool:
        """."""
        user_display: str = str(booking.user)
        agent_display: str = str(booking.agent) if booking.agent_id else str()
        reason_display: str = booking.decrement_reason if booking.decrement_reason else str()
        if booking.agent_id:
            message: str = self.agent_normalized_template.format(
                user_display=user_display, commission=booking.commission
            )
            if reason_display:
                message += f" Причина: {reason_display}"
            data: dict[str, Any] = dict(
                message=message, created=datetime.now(tz=UTC), user_id=booking.agent_id
            )
            await self.notification_repo.create(data=data)
        if booking.agency_id:
            if booking.agent_id:
                message: str = self.agency_normalized_template_one.format(
                    user_display=user_display,
                    agent_display=agent_display,
                    commission=booking.commission,
                )
            else:
                message: str = self.agency_normalized_template_two.format(
                    user_display=user_display, commission=booking.commission
                )
            if reason_display:
                message += f" Причина: {reason_display}"
            data: dict[str, Any] = dict(
                message=message, created=datetime.now(tz=UTC), agency_id=booking.agency_id
            )
            await self.notification_repo.create(data=data)
        return True
