from typing import Type, Any, Union

from ..entities import BaseAgentCase
from ..repos import AgentRepo, User
from ..types import AgentPagination, AgentBookingRepo, AgentUserRepo


class RepresesAgentsListCase(BaseAgentCase):
    """
    Список агентов представителя агенства
    """

    def __init__(
        self,
        user_type: str,
        booking_substages: Any,
        agent_repo: Type[AgentRepo],
        user_repo: Type[AgentUserRepo],
        booking_repo: Type[AgentBookingRepo],
    ) -> None:
        self.agent_repo: AgentRepo = agent_repo()
        self.user_repo: AgentUserRepo = user_repo()
        self.booking_repo: AgentBookingRepo = booking_repo()

        self.user_type: str = user_type
        self.booking_substages: Any = booking_substages

    async def __call__(
        self, agency_id: int, pagination: AgentPagination, init_filters: dict[str, Any]
    ) -> dict[str, Any]:
        filters: dict[str, Any] = dict(
            active=True,
            agent_id=self.agent_repo.a_builder.build_outer("id"),
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
            agent_id=self.agent_repo.a_builder.build_outer("id"),
            amocrm_substage__in=[
                self.booking_substages.REALIZED,
                self.booking_substages.MONEY_PROCESS,
            ],
        )
        succeed_booking_qs: Any = self.booking_repo.exists(filters=filters)
        ordering: str = init_filters.pop("ordering", "-id")
        search: list[list[dict[str, Any]]] = init_filters.pop("search", list())
        filters: dict[str, Any] = dict(agency_id=agency_id, type=self.user_type, is_deleted=False)
        if len(search) == 1:
            q_filters: list[Any] = [self.agent_repo.q_builder(or_filters=search[0])]
        else:
            q_base: Any = self.agent_repo.q_builder()
            for s in search:
                q_base |= self.agent_repo.q_builder(and_filters=s)
            q_filters: list[Any] = [q_base]
        annotations: dict[str, Any] = dict(
            active_clients=self.agent_repo.a_builder.build_scount(
                active_booking_qs
            ),
            succeed_clients=self.agent_repo.a_builder.build_scount(
                succeed_booking_qs
            ),
        )
        agents: list[User] = await self.agent_repo.list(
            filters=filters,
            ordering=ordering,
            end=pagination.end,
            q_filters=q_filters,
            start=pagination.start,
            annotations=annotations,
        )
        counted: list[tuple[Union[int, str]]] = await self.agent_repo.count(
            filters=filters, q_filters=q_filters
        )
        count: int = len(counted)
        if count and count == 1:
            count: int = counted[0][0]
        data: dict[str, Any] = dict(count=count, result=agents, page_info=pagination(count=count))
        return data
