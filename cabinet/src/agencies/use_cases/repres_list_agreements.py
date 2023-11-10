from typing import Any, Optional, Type, Union

from src.agents.repos import AgentRepo, User
from src.agreements.repos import AgencyAgreementRepo
from tortoise.queryset import QuerySet

from ..entities import BaseAgencyCase
from ..exceptions import AgencyNotFoundError
from ..repos import Agency, AgencyRepo
from ..types import AgencyPagination


class ListAgreementsCase(BaseAgencyCase):
    """
    Получение договоров
    """

    def __init__(
        self,
        agency_repo: Type[AgencyRepo],
        agreement_repo: Type[AgencyAgreementRepo],
        agent_repo: Type[AgentRepo],
    ):
        self.agency_repo: AgencyRepo = agency_repo()
        self.agreement_repo: AgencyAgreementRepo = agreement_repo()
        self.agent_repo: AgentRepo = agent_repo()

    async def __call__(
        self,
        pagination: AgencyPagination,
        init_filters: dict[str, Any],
        repres_id: Optional[int] = None,
        agent_id: Optional[int] = None,
    ) -> dict[str, Any]:
        ordering: Union[str, None] = init_filters.pop("ordering", "-id")
        search: list[list[dict[str, Any]]] = init_filters.pop("search", [])
        if len(search) == 1:
            q_filters: list[Any] = [self.agreement_repo.q_builder(or_filters=search[0])]
        else:
            q_base: Any = self.agreement_repo.q_builder()
            for s in search:
                q_base |= self.agreement_repo.q_builder(and_filters=s)
            q_filters: list[Any] = [q_base]

        if repres_id:
            agency: Agency = await self.agency_repo.retrieve(filters=dict(maintainer=repres_id))
        else:
            agent: User = await self.agent_repo.retrieve(filters=dict(id=agent_id), related_fields=["agency"])
            agency: Agency = await agent.agency
        if not agency:
            raise AgencyNotFoundError
        select_related = ["status", "agreement_type", "agency"]
        agreements_query: QuerySet = self.agreement_repo.list(
            ordering=ordering,
            q_filters=q_filters,
            filters=dict(agency_id=agency.id),
            related_fields=select_related,
            start=pagination.start,
            end=pagination.end,
        )
        count: int = await self.agreement_repo.count(
            q_filters=q_filters,
            filters=dict(agency_id=agency.id),
        )
        agreements = await agreements_query
        data: dict[str, Any] = dict(count=count, result=agreements, page_info=pagination(count=count))
        return data
