from typing import Any, Optional, Type

from src.agents.repos import AgentRepo, User
from src.agreements.repos import (AgencyAdditionalAgreement,
                                  AgencyAdditionalAgreementRepo)

from ..entities import BaseAgencyCase
from ..exceptions import AdditionalAgreementNotExists
from ..repos import Agency, AgencyRepo


class AdditionalAgreementCase(BaseAgencyCase):
    """
    Получение дополнительного соглашения
    """

    def __init__(
        self,
        additional_agreement_repo: Type[AgencyAdditionalAgreementRepo],
        agency_repo: Type[AgencyRepo],
        agent_repo: Type[AgentRepo],
    ):
        self.additional_agreement_repo: AgencyAdditionalAgreementRepo = additional_agreement_repo()
        self.agency_repo: AgencyRepo = agency_repo()
        self.agent_repo: AgentRepo = agent_repo()

    async def __call__(
        self,
        additional_id: int,
        agent_id: Optional[int] = None,
        repres_id: Optional[int] = None,
    ) -> AgencyAdditionalAgreement:

        if repres_id:
            agency: Agency = await self.agency_repo.retrieve(filters=dict(maintainer=repres_id))
        else:
            agent: User = await self.agent_repo.retrieve(
                filters=dict(id=agent_id),
                related_fields=["agency"]
            )
            agency: Agency = await agent.agency

        filters: dict[str, Any] = dict(id=additional_id, agency_id=agency.id)
        select_related = ["status", "agency"]
        additional_agreement: AgencyAdditionalAgreement = await self.additional_agreement_repo.retrieve(
            filters=filters,
            related_fields=select_related,
        )

        if not additional_agreement:
            raise AdditionalAgreementNotExists

        return additional_agreement
