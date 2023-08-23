from typing import Type, Any

from ..entities import BaseAgentCase
from ..exceptions import AgentNotFoundError
from ..repos import AgentRepo, User
from ..types import AgentUserRepo, AgentBookingRepo, AgentCheckRepo


class RepresesAgentsRetrieveCase(BaseAgentCase):
    """
    Агент представителя агенства
    """

    def __init__(
        self,
        user_types: Any,
        booking_substages: Any,
        agent_repo: Type[AgentRepo],
        user_repo: Type[AgentUserRepo],
        check_repo: Type[AgentCheckRepo],
        booking_repo: Type[AgentBookingRepo],
    ) -> None:
        self.agent_repo: AgentRepo = agent_repo()
        self.user_repo: AgentUserRepo = user_repo()
        self.check_repo: AgentCheckRepo = check_repo()
        self.booking_repo: AgentBookingRepo = booking_repo()

        self.user_types: Any = user_types
        self.booking_substages: Any = booking_substages

    async def __call__(self, agency_id: int, agent_id: int) -> User:
        filters: dict[str, Any] = dict(
            active=True,
            agent_id=agent_id,
            user_id=self.user_repo.a_builder.build_outer("id"),
            amocrm_substage__not_in=[
                self.booking_substages.REALIZED,
                self.booking_substages.UNREALIZED,
                self.booking_substages.TERMINATION,
                self.booking_substages.MONEY_PROCESS,
            ],
        )
        active_booking_qs: Any = self.booking_repo.exists(filters=filters)
        filters: dict[str, Any] = dict(
            active=True,
            agent_id=agent_id,
            user_id=self.user_repo.a_builder.build_outer("id"),
            amocrm_substage__in=[
                self.booking_substages.REALIZED,
                self.booking_substages.MONEY_PROCESS,
            ],
        )
        succeed_booking_qs: Any = self.booking_repo.exists(filters=filters)
        filters: dict[str, Any] = dict(
            active=True,
            agent_id=agent_id,
            user_id=self.user_repo.a_builder.build_outer("id"),
            amocrm_substage__in=[
                self.booking_substages.UNREALIZED,
                self.booking_substages.TERMINATION,
            ],
        )
        closed_booking_qs: Any = self.booking_repo.exists(filters=filters)

        filters: dict[str, Any] = dict(agent_id=agent_id)
        active_filters: dict[str, Any] = dict(active_booking=True)
        annotations: dict[str, Any] = dict(
            active_booking=self.user_repo.a_builder.build_exists(active_booking_qs)
        )
        active_clients_qs: Any = self.user_repo.list(filters=filters, annotations=annotations)
        filters: dict[str, Any] = dict(agent_id=agent_id)
        succeed_filters: dict[str, Any] = dict(succeed_booking=True)
        annotations: dict[str, Any] = dict(
            succeed_booking=self.user_repo.a_builder.build_exists(succeed_booking_qs)
        )
        succeed_clients_qs: Any = self.user_repo.list(filters=filters, annotations=annotations)
        filters: dict[str, Any] = dict(agent_id=agent_id)
        closed_filters: dict[str, Any] = dict(closed_booking=True)
        annotations: dict[str, Any] = dict(
            closed_booking=self.user_repo.a_builder.build_exists(closed_booking_qs)
        )
        closed_clients_qs: Any = self.user_repo.list(filters=filters, annotations=annotations)

        filters: dict[str, Any] = dict(agency_id=agency_id, agent_id=agent_id)
        check_qs: Any = self.check_repo.list(filters=filters, related_fields=["unique_status"])
        filters: dict[str, Any] = dict(
            agent_id=agent_id, agency_id=agency_id, type=self.user_types.CLIENT, is_deleted=False
        )
        prefetch_fields: list[Any] = [
            dict(relation="users_checks", queryset=check_qs, to_attr="checks")
        ]
        users_qs: Any = self.user_repo.list(filters=filters, prefetch_fields=prefetch_fields)

        filters: dict[str, Any] = dict(id=agent_id, agency_id=agency_id, type=self.user_types.AGENT)
        prefetch_fields: list[Any] = [dict(relation="users", queryset=users_qs, to_attr="clients")]
        annotations: dict[str, Any] = dict(
            closed_clients=self.agent_repo.a_builder.build_scount(
                closed_clients_qs, filters=closed_filters
            ),
            active_clients=self.agent_repo.a_builder.build_scount(
                active_clients_qs, filters=active_filters
            ),
            succeeded_clients=self.agent_repo.a_builder.build_scount(
                succeed_clients_qs, filters=succeed_filters
            ),
        )
        agent: User = await self.agent_repo.retrieve(
            filters=filters, prefetch_fields=prefetch_fields, annotations=annotations
        )
        if not agent:
            raise AgentNotFoundError
        return agent
