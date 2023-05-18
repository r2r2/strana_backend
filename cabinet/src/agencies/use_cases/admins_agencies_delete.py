from typing import Type, Any

from src.users.loggers.wrappers import user_changes_logger
from ..loggers.wrappers import agency_changes_logger
from ..entities import BaseAgencyCase
from ..exceptions import AgencyNotFoundError
from ..repos import Agency, AgencyRepo
from ..types import AgencyAgentRepo, AgencyCheckRepo, AgencyRedis, AgencyRepresRepo, AgencyUserRepo


class AdminsAgenciesDeleteCase(BaseAgencyCase):
    """
    Удаление агентства администратором
    """

    def __init__(
        self,
        user_types: Any,
        redis: AgencyRedis,
        redis_config: dict[str, Any],
        agency_repo: Type[AgencyRepo],
        user_repo: Type[AgencyUserRepo],
        check_repo: Type[AgencyCheckRepo],
        agent_repo: Type[AgencyAgentRepo],
        repres_repo: Type[AgencyRepresRepo],
    ) -> None:
        self.agency_repo: AgencyRepo = agency_repo()
        self.agency_update = agency_changes_logger(
            self.agency_repo.update, self, content="Обновление данных агентства is_deleted=True"
        )
        self.user_repo: AgencyUserRepo = user_repo()
        self.user_update = user_changes_logger(
            self.user_repo.update, self, content="Открепление клиента от агента и агентства"
        )
        self.check_repo: AgencyCheckRepo = check_repo()
        self.agent_repo: AgencyAgentRepo = agent_repo()
        self.agent_update = user_changes_logger(
            self.agent_repo.update, self, content="Помечаем агентов is_deleted"
        )
        self.repres_repo: AgencyRepresRepo = repres_repo()
        self.repres_update = user_changes_logger(
            self.repres_repo.update, self, content="Помечаем представителей is_deleted"
        )
        self.redis: AgencyRedis = redis
        self.user_types: Any = user_types
        self.deleted_users_key: str = redis_config["deleted_users_key"]

    async def __call__(self, agency_id: int) -> Agency:
        deleted_users: list[int] = list()
        filters = dict(id=agency_id, is_deleted=False)
        agency = await self.agency_repo.retrieve(filters=filters)
        if not agency:
            raise AgencyNotFoundError

        data = dict(is_deleted=True)
        agency = await self.agency_update(agency=agency, data=data)

        # Маркируем удалёнными агентов
        filters = dict(agency_id=agency_id, type=self.user_types.AGENT, is_deleted=False)
        agents = await self.agent_repo.list(filters=filters)
        for agent in agents:
            deleted_users.append(agent.id)
            await self.agent_update(agent, data=data)

        # Маркируем удалённым представителя
        filters = dict(agency_id=agency_id, type=self.user_types.REPRES, is_deleted=False)
        represes = await self.repres_repo.list(filters=filters)
        for repres in represes:
            deleted_users.append(repres.id)
            await self.repres_update(repres, data=data)

        # Снимаем с клиентов привязку к агенту и агентству
        filters = dict(agency_id=agency_id, type=self.user_types.CLIENT)
        users = await self.user_repo.list(filters=filters)
        data = dict(agency_id=None, agent_id=None)
        for user in users:
            await self.user_update(user=user, data=data)

        # Удаляем проверки по агентству
        filters = dict(agency_id=agency_id)
        checks = await self.check_repo.list(filters=filters)
        for check in checks:
            await self.check_repo.delete(check)

        # Удаляем проверки по агентам
        agents_ids = list(agent.id for agent in agents)
        filters = dict(agent_id__in=agents_ids)
        checks = await self.check_repo.list(filters=filters)
        for check in checks:
            await self.check_repo.delete(check)

        await self.redis.append(self.deleted_users_key, deleted_users)
        return agency
