from typing import Any, Type

from src.booking.loggers.wrappers import booking_changes_logger
from src.users.loggers.wrappers import user_changes_logger

from ..entities import BaseAgentCase
from ..exceptions import AgentNotFoundError
from ..repos import AgentRepo, User
from ..types import AgentBookingRepo, AgentCheckRepo, AgentRedis, AgentUserRepo


class RepresesAgentsDeleteCase(BaseAgentCase):
    """
    Удаление агента представителем агентсва
    """

    def __init__(
        self,
        user_types: Any,
        redis: AgentRedis,
        agent_repo: Type[AgentRepo],
        redis_config: dict[str, Any],
        user_repo: Type[AgentUserRepo],
        check_repo: Type[AgentCheckRepo],
        booking_repo: Type[AgentBookingRepo],
    ) -> None:
        self.agent_repo: AgentRepo = agent_repo()
        self.agent_update = user_changes_logger(
            self.agent_repo.update, self, content="Помечаем агента удалённым"
        )
        self.user_repo: AgentUserRepo = user_repo()
        self.user_update = user_changes_logger(
            self.user_repo.update, self, content="Отвязываем клиентов от агента"
        )
        self.check_repo: AgentCheckRepo = check_repo()
        self.booking_repo: AgentBookingRepo = booking_repo()

        self.redis: AgentRedis = redis
        self.user_types: Any = user_types
        self.deleted_users_key: str = redis_config["deleted_users_key"]
        self.booking_update = booking_changes_logger(
            self.booking_repo.update, self, content="Удаление агента",
        )

    async def __call__(self, agent_id: int, agency_id: int) -> User:
        filters = dict(
            id=agent_id, agency_id=agency_id, is_deleted=False, type=self.user_types.AGENT
        )
        agent: User = await self.agent_repo.retrieve(filters=filters)
        if not agent:
            raise AgentNotFoundError

        # Маркируем удалённым агента
        data = dict(is_deleted=True)
        agent = await self.agent_update(agent, data=data)

        # Отвязываем клиентов от агента
        filters = dict(agent_id=agent.id, agency_id=agency_id, type=self.user_types.CLIENT)
        users = await self.user_repo.list(filters=filters)
        data = dict(agent_id=None)
        for user in users:
            await self.user_update(user=user, data=data)

        # Удаляем проверки
        filters = dict(agent_id=agent.id)
        checks = await self.check_repo.list(filters=filters)
        for check in checks:
            if not check.agency_id:
                await self.check_repo.delete(check)
            else:
                await self.check_repo.update(check, data=data)

        filters = dict(agent_id=agent.id)
        bookings = await self.booking_repo.list(filters=filters)
        data = dict(agent_id=None)
        for booking in bookings:
            await self.booking_update(booking=booking, data=data)

        await self.redis.append(self.deleted_users_key, agent.id)
        return agent
