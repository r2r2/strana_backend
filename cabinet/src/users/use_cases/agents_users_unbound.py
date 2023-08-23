from typing import Any, Type

from src.booking.loggers.wrappers import booking_changes_logger

from ..constants import UserStatus, UserType
from ..entities import BaseUserCase
from ..exceptions import UserNotFoundError
from ..loggers.wrappers import user_changes_logger
from ..repos import Check, CheckRepo, User, UserRepo
from ..types import UserBooking, UserBookingRepo


class AgentsUsersUnboundCase(BaseUserCase):
    """
    Отвязка пользователя агента
    """

    def __init__(
        self,
        user_repo: Type[UserRepo],
        check_repo: Type[CheckRepo],
        booking_repo: Type[UserBookingRepo],
    ) -> None:
        self.user_repo: UserRepo = user_repo()
        self.user_update = user_changes_logger(self.user_repo.update, self, content="Отвязка клиента от агента")
        self.check_repo: CheckRepo = check_repo()
        self.booking_repo: UserBookingRepo = booking_repo()
        self.booking_update = booking_changes_logger(
            self.booking_repo.update, self, content="Отвязка пользователя",
        )

    async def __call__(self, agent_id: int, user_id: int) -> None:
        filters: dict[str, Any] = dict(user_id=user_id, agent_id=agent_id)
        check: Check = await self.check_repo.retrieve(filters=filters, related_fields=["unique_status"])
        filters: dict[str, Any] = dict(id=user_id, type=UserType.CLIENT)
        user: User = await self.user_repo.retrieve(filters=filters)
        if not check or not user:
            raise UserNotFoundError
        if check.unique_status and check.unique_status.slug == UserStatus.UNIQUE:
            data: dict[str, Any] = dict(agent_id=None)
            await self.check_repo.update(check, data=data)
        else:
            await self.check_repo.delete(check)
        if user.agent_id and str(user.agent_id) == str(agent_id):
            data: dict[str, Any] = dict(agent_id=None)
            user: User = await self.user_update(user=user, data=data)
        filters: dict[str, Any] = dict(user_id=user.id, agent_id=agent_id)
        bookings: list[UserBooking] = await self.booking_repo.list(filters=filters)
        for booking in bookings:
            data: dict[str, Any] = dict(agent_id=None, comission=booking.start_commission)
            await self.booking_update(booking=booking, data=data)
