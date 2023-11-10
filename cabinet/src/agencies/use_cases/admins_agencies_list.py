from typing import Any, Type, Union

from ..entities import BaseAgencyCase
from ..repos import Agency, AgencyRepo
from ..types import (AgencyAgentRepo, AgencyBookingRepo, AgencyPagination,
                     AgencyUserRepo)


class AdminsAgenciesListCase(BaseAgencyCase):
    """
    Список агенств администратором
    """

    def __init__(
        self,
        user_types: Any,
        booking_substages: Any,
        agency_repo: Type[AgencyRepo],
        user_repo: Type[AgencyUserRepo],
        agent_repo: Type[AgencyAgentRepo],
        booking_repo: Type[AgencyBookingRepo],
    ) -> None:
        self.user_repo: AgencyUserRepo = user_repo()
        self.agency_repo: AgencyRepo = agency_repo()
        self.agent_repo: AgencyAgentRepo = agent_repo()
        self.booking_repo: AgencyBookingRepo = booking_repo()

        self.user_types: Any = user_types
        self.booking_substages: Any = booking_substages

    async def __call__(
        self, pagination: AgencyPagination, init_filters: dict[str, Any]
    ) -> dict[str, Any]:
        filters: dict[str, Any] = dict(
            active=True,
            agency_id=self.agency_repo.a_builder.build_outer("id"),
            amocrm_substage__not_in=[
                self.booking_substages.REALIZED,
                self.booking_substages.UNREALIZED,
                self.booking_substages.TERMINATION,
                self.booking_substages.MONEY_PROCESS,
            ],
        )
        active_booking_qs: Any = self.booking_repo.exists(filters=filters)

        filters: dict[str, Any] = dict(
            agency_id=self.agency_repo.a_builder.build_outer("id"),
            type=self.user_types.AGENT,
            is_deleted=False,
        )
        active_agents_qs: Any = self.agent_repo.list(filters=filters)

        ordering: Union[str, None] = init_filters.pop("ordering", "-id")
        search: list[list[dict[str, Any]]] = init_filters.pop("search", [])
        if len(search) == 1:
            q_filters: list[Any] = [self.agency_repo.q_builder(or_filters=search[0])]
        else:
            q_base: Any = self.agency_repo.q_builder()
            for s in search:
                q_base |= self.agency_repo.q_builder(and_filters=s)
            q_filters: list[Any] = [q_base]
        filters: dict[str, Any] = dict(is_deleted=False, **init_filters)
        annotations: dict[str, Any] = dict(
            active_agents=self.agency_repo.a_builder.build_scount(active_agents_qs),
            active_clients=self.agency_repo.a_builder.build_scount(
                active_booking_qs
            ),
        )
        agencies: list[Agency] = await self.agency_repo.list(
            start=pagination.start,
            end=pagination.end,
            filters=filters,
            ordering=ordering,
            q_filters=q_filters,
            annotations=annotations,
            prefetch_fields=["maintainer"],
        )
        count: int = await self.agency_repo.count(
            filters=filters, q_filters=q_filters
        )

        data: dict[str, Any] = dict(count=count, result=agencies, page_info=pagination(count=count))
        return data
