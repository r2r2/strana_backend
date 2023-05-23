from typing import Any, Type
from enum import IntEnum

from src.booking.loggers.wrappers import booking_changes_logger

from ..entities import BaseUserCase
from ..exceptions import UserNoAgentError, UserNotFoundError
from ..loggers.wrappers import user_changes_logger
from ..models import RequestRepresesUsersReboundModel
from ..repos import CheckRepo, User, UserRepo
from ..types import UserAgentRepo, UserBooking, UserBookingRepo


class LeadStatuses(IntEnum):
    """
     Статусы закрытых сделок в амо.
    """
    REALIZED: int = 142  # Успешно реализовано
    UNREALIZED: int = 143  # Закрыто и не реализовано


class RepresesUsersReboundCase(BaseUserCase):
    """
    Перепривязка пользователя представителем агентства
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
        self.check_repo: CheckRepo = check_repo()
        self.agent_repo: UserAgentRepo = agent_repo()
        self.booking_repo: UserBookingRepo = booking_repo()

        self.change_client_agent_task: Any = change_client_agent_task

        self.user_reassign = user_changes_logger(
            self.user_repo.update, self, content="Перепривязка пользователя к представителю агентства"
        )
        self.booking_update = booking_changes_logger(
            self.booking_repo.update, self, content="Подписание ДДУ",
        )

    async def __call__(
        self, user_id: int, agency_id: int, payload: RequestRepresesUsersReboundModel
    ) -> User:
        data: dict[str, Any] = payload.dict()
        to_agent_id: int = data["to_agent_id"]
        from_agent_id: int = data["from_agent_id"]
        filters: dict[str, Any] = dict(id=to_agent_id, agency_id=agency_id, is_deleted=False)
        to_agent: User = await self.agent_repo.retrieve(filters=filters)
        filters: dict[str, Any] = dict(id=from_agent_id, agency_id=agency_id, is_deleted=False)
        from_agent: User = await self.agent_repo.retrieve(filters=filters)
        if not to_agent or not from_agent:
            raise UserNoAgentError
        filters: dict[str, Any] = dict(id=user_id, agent_id=from_agent.id)
        user: User = await self.user_repo.retrieve(filters=filters)
        if not user:
            raise UserNotFoundError

        data: dict[str, Any] = dict(agent_id=to_agent.id)
        user: User = await self.user_reassign(user=user, data=data)

        filters: dict[str, Any] = dict(user_id=user.id, agent_id=from_agent.id, agency_id=agency_id)
        bookings: list[UserBooking] = await self.booking_repo.list(filters=filters).exclude(
            amocrm_status_id=LeadStatuses.REALIZED,
        ).exclude(
            amocrm_status_id=LeadStatuses.UNREALIZED,
        )

        for booking in bookings:
            data: dict[str, Any] = dict(
                agent_id=to_agent.id,
                agency_id=agency_id,
            )
            await self.booking_update(booking=booking, data=data)
        self.change_client_agent_task.delay(user_id=user_id, agent_id=to_agent_id)
        return user
