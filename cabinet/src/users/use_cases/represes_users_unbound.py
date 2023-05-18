from typing import Any, Type

from src.booking.loggers.wrappers import booking_changes_logger

from ..constants import UserStatus, UserType
from ..entities import BaseUserCase
from ..exceptions import UserNoAgentError, UserNotFoundError
from ..loggers.wrappers import user_changes_logger
from ..models import RequestRepresesUsersUnboundModel
from ..repos import Check, CheckRepo, User, UserRepo
from ..types import UserAgentRepo, UserBooking, UserBookingRepo


class RepresesUsersUnboundCase(BaseUserCase):
    """
    Отвязка пользователя представителем агентства
    """

    def __init__(
        self,
        user_repo: Type[UserRepo],
        check_repo: Type[CheckRepo],
        agent_repo: Type[UserAgentRepo],
        booking_repo: Type[UserBookingRepo],
    ) -> None:
        self.user_repo: UserRepo = user_repo()
        self.user_unbound = user_changes_logger(self.user_repo.update, self, content="Отвязка пользователя от агента")
        self.check_repo: CheckRepo = check_repo()
        self.agent_repo: UserAgentRepo = agent_repo()
        self.booking_repo: UserBookingRepo = booking_repo()
        self.booking_update = booking_changes_logger(self.booking_repo.update, self, content="Отвязка пользователя")

    async def __call__(
        self, agency_id: int, user_id: int, payload: RequestRepresesUsersUnboundModel
    ) -> User:
        data: dict[str, Any] = payload.dict()
        agent_id: int = data["agent_id"]
        filters: dict[str, Any] = dict(id=agent_id, type=UserType.AGENT, agency_id=agency_id)
        agent: User = await self.agent_repo.retrieve(filters=filters)
        if not agent:
            raise UserNoAgentError
        filters: dict[str, Any] = dict(
            user_id=user_id, agency_id=agency_id, agent_id=agent_id, status=UserStatus.UNIQUE
        )
        check: Check = await self.check_repo.retrieve(filters=filters)
        filters: dict[str, Any] = dict(
            id=user_id, agent_id=agent_id, agency_id=agency_id, type=UserType.CLIENT
        )
        user: User = await self.user_repo.retrieve(filters=filters)
        if not check or not user:
            raise UserNotFoundError
        data: dict[str, Any] = dict(agent_id=None)
        await self.check_repo.update(check, data=data)
        data: dict[str, Any] = dict(agent_id=None)
        user: User = await self.user_unbound(user=user, data=data)
        filters: dict[str, Any] = dict(user_id=user.id, agent_id=agent_id)
        bookings: list[UserBooking] = await self.booking_repo.list(filters=filters)
        for booking in bookings:
            data: dict[str, Any] = dict(agent_id=None, comission=booking.start_commission)
            await self.booking_update(booking=booking, data=data)
        return user
