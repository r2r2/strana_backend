from typing import Any, Type

from src.booking.loggers.wrappers import booking_changes_logger

from ..constants import UserStatus, UserType
from ..entities import BaseUserCase
from ..exceptions import UserNoAgentError, UserNotFoundError
from ..loggers.wrappers import user_changes_logger
from ..models import RequestRepresesUsersBoundModel
from src.users.repos import Check, CheckRepo, User, UserRepo, UniqueStatus
from ..types import UserAgentRepo, UserBooking, UserBookingRepo
from src.users.utils import get_unique_status


class RepresesUsersBoundCase(BaseUserCase):
    """
    Привязка пользователя представителем агентства
    """

    def __init__(
        self,
        user_repo: Type[UserRepo],
        check_repo: Type[CheckRepo],
        change_client_agent_task: Any,
        agent_repo: Type[UserAgentRepo],
        booking_repo: Type[UserBookingRepo],
    ) -> None:
        self.user_repo: UserRepo = user_repo()
        self.user_assign = user_changes_logger(self.user_repo.update, self, content="Привязка пользователя к агенту")
        self.check_repo: CheckRepo = check_repo()
        self.agent_repo: UserAgentRepo = agent_repo()
        self.booking_repo: UserBookingRepo = booking_repo()
        self.change_client_agent_task: Any = change_client_agent_task
        self.booking_update = booking_changes_logger(self.booking_repo.update, self, content="Привязка пользователя")

    async def __call__(
        self, agency_id: int, user_id: int, payload: RequestRepresesUsersBoundModel
    ) -> None:
        data: dict[str, Any] = payload.dict()
        agent_id: int = data["agent_id"]
        filters: dict[str, Any] = dict(id=agent_id, type=UserType.AGENT, agency_id=agency_id)
        agent: User = await self.agent_repo.retrieve(filters=filters)
        if not agent:
            raise UserNoAgentError
        unique_status: UniqueStatus = await get_unique_status(slug=UserStatus.UNIQUE)
        filters: dict[str, Any] = dict(
            user_id=user_id, agency_id=agency_id, unique_status=unique_status, agent_id=None
        )
        check: Check = await self.check_repo.retrieve(filters=filters)
        filters: dict[str, Any] = dict(
            id=user_id, agency_id=agency_id, type=UserType.CLIENT, agent_id=None
        )
        user: User = await self.user_repo.retrieve(filters=filters)
        if not check or not user:
            raise UserNotFoundError
        data: dict[str, Any] = dict(agent_id=agent_id, agency_id=agency_id)
        await self.user_assign(user=user, data=data)
        data: dict[str, Any] = dict(agent_id=agent_id)
        await self.check_repo.update(check, data=data)
        filters: dict[str, Any] = dict(user_id=user.id, agency_id=agency_id, agent_id=None)
        bookings: list[UserBooking] = await self.booking_repo.list(filters=filters)
        for booking in bookings:
            data: dict[str, Any] = dict(agent_id=agent_id, comission=booking.start_commission)
            await self.booking_update(booking=booking, data=data)
        self.change_client_agent_task.delay(user_id=user_id, agent_id=agent_id)
