from typing import Type, Any

from ..types import AgencyAgentRepo, AgencyUserRepo, AgencyBookingRepo
from ..entities import BaseAgencyCase
from ..repos import AgencyRepo, Agency
from ..exceptions import AgencyNotFoundError


class AdminsAgenciesRetrieveCase(BaseAgencyCase):
    """
    Детальное Агентство администратором
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
        self.agency_repo: AgencyRepo = agency_repo()
        self.user_repo: AgencyUserRepo = user_repo()
        self.agent_repo: AgencyAgentRepo = agent_repo()
        self.booking_repo: AgencyBookingRepo = booking_repo()

        self.user_types: Any = user_types
        self.booking_substages: Any = booking_substages

    async def __call__(self, agency_id: int) -> Agency:
        filters: dict[str, Any] = dict(
            active=True,
            agency_id=self.booking_repo.a_builder.build_outer("agency_id"),
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
            agency_id=self.booking_repo.a_builder.build_outer("agency_id"),
            amocrm_substage__in=[
                self.booking_substages.REALIZED,
                self.booking_substages.MONEY_PROCESS,
            ],
        )
        succeed_booking_qs: Any = self.booking_repo.exists(filters=filters)
        filters: dict[str, Any] = dict(
            active=True,
            agency_id=self.booking_repo.a_builder.build_outer("agency_id"),
            amocrm_substage__in=[
                self.booking_substages.UNREALIZED,
                self.booking_substages.TERMINATION,
            ],
        )
        closed_booking_qs: Any = self.booking_repo.exists(filters=filters)

        filters: dict[str, Any] = dict(agency_id=self.user_repo.a_builder.build_outer("id"))
        active_filters: dict[str, Any] = dict(active_booking=True)
        annotations: dict[str, Any] = dict(
            active_booking=self.user_repo.a_builder.build_exists(active_booking_qs)
        )
        active_clients_qs: Any = self.user_repo.list(filters=filters, annotations=annotations)
        filters: dict[str, Any] = dict(agency_id=self.user_repo.a_builder.build_outer("id"))
        succeed_filters: dict[str, Any] = dict(succeed_booking=True)
        annotations: dict[str, Any] = dict(
            succeed_booking=self.user_repo.a_builder.build_exists(succeed_booking_qs)
        )
        succeed_clients_qs: Any = self.user_repo.list(filters=filters, annotations=annotations)
        filters: dict[str, Any] = dict(agency_id=self.user_repo.a_builder.build_outer("id"))
        closed_filters: dict[str, Any] = dict(closed_booking=True)
        annotations: dict[str, Any] = dict(
            closed_booking=self.user_repo.a_builder.build_exists(closed_booking_qs)
        )
        closed_clients_qs: Any = self.user_repo.list(filters=filters, annotations=annotations)

        filters: dict[str, Any] = dict(
            agency_id=agency_id, type=self.user_types.AGENT, is_deleted=False
        )
        agents_qs: Any = self.agent_repo.list(filters=filters)
        filters: dict[str, Any] = dict(id=agency_id)
        annotations: dict[str, Any] = dict(
            closed_clients=self.agent_repo.a_builder.build_scount(
                closed_clients_qs, filters=closed_filters
            ),
            active_clients=self.agent_repo.a_builder.build_scount(
                active_clients_qs, filters=active_filters
            ),
            succeed_clients=self.agent_repo.a_builder.build_scount(
                succeed_clients_qs, filters=succeed_filters
            ),
        )
        agency: Agency = await self.agency_repo.retrieve(
            filters=filters,
            annotations=annotations,
            prefetch_fields=[
                "maintainer",
                dict(relation="users", queryset=agents_qs, to_attr="agents"),
            ],
        )
        if not agency:
            raise AgencyNotFoundError
        return agency
