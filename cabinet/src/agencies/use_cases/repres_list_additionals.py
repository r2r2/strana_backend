from typing import Any, Optional, Type, Union

from src.agents.repos import AgentRepo, User
from src.agreements.repos import AgencyAdditionalAgreementRepo, AgencyAgreementRepo
from tortoise.queryset import QuerySet

from ..entities import BaseAgencyCase
from ..exceptions import AgencyNotFoundError
from ..repos import Agency, AgencyRepo
from ..types import AgencyPagination


class ListAdditionalAgreementsCase(BaseAgencyCase):
    """
    Получение дополнительных соглашений
    """

    def __init__(
        self,
        agency_repo: Type[AgencyRepo],
        agent_repo: Type[AgentRepo],
        additional_agreement_repo: Type[AgencyAdditionalAgreementRepo],
    ):
        self.agency_repo: AgencyRepo = agency_repo()
        self.agent_repo: AgentRepo = agent_repo()
        self.additional_agreement_repo = additional_agreement_repo()

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
            q_filters: list[Any] = [self.additional_agreement_repo.q_builder(or_filters=search[0])]
        else:
            q_base: Any = self.additional_agreement_repo.q_builder()
            for s in search:
                q_base |= self.additional_agreement_repo.q_builder(and_filters=s)
            q_filters: list[Any] = [q_base]

        if repres_id:
            agency: Agency = await self.agency_repo.retrieve(filters=dict(maintainer=repres_id))
        else:
            agent: User = await self.agent_repo.retrieve(
                filters=dict(id=agent_id), related_fields=["agency"]
            )
            agency: Agency = await agent.agency

        if not agency:
            raise AgencyNotFoundError

        select_related = ["status", "agency"]
        additional_agreements = await self.additional_agreement_repo.list(
            start=pagination.start,
            end=pagination.end,
            ordering=ordering,
            q_filters=q_filters,
            filters=dict(agency_id=agency.id),
            related_fields=select_related,
        )
        counted = await self.additional_agreement_repo.list(
            q_filters=q_filters,
            filters=dict(agency_id=agency.id),
        ).count()

        data: dict[str, Any] = dict(count=counted, result=additional_agreements, page_info=pagination(count=counted))

        return data
