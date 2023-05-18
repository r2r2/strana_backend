from typing import Any, Type, Optional

from src.agencies.exceptions import AgencyAgreementNotExists
from src.agreements.repos import AgencyAgreement, AgencyAgreementRepo
from src.users.repos import User

from ..entities import BaseAgencyCase
from ..types import AgencyUserRepo


class AgreementCase(BaseAgencyCase):
    """
    Получение договора
    """

    def __init__(
        self,
        agreement_repo: Type[AgencyAgreementRepo],
        agent_repo: Type[AgencyUserRepo],
    ):
        self.agreement_repo: AgencyAgreementRepo = agreement_repo()
        self.agent_repo: AgencyUserRepo = agent_repo()

    async def __call__(
        self,
        agreement_id: int,
        agent_id: Optional[int] = None,
        repres_id: Optional[int] = None
    ) -> AgencyAgreement:

        if agent_id:
            agent: User = await self.agent_repo.retrieve(filters=dict(id=agent_id), related_fields=["agency"])
            filters: dict[str, Any] = dict(id=agreement_id, agency_id=agent.agency.id)
        else:
            repres: User = await self.agent_repo.retrieve(filters=dict(id=repres_id), related_fields=["agency"])
            filters: dict[str, Any] = dict(id=agreement_id, agency_id=repres.agency.id)

        select_related = ["status", "agreement_type", "agency"]
        agreement: AgencyAgreement = await self.agreement_repo.retrieve(filters=filters, related_fields=select_related)
        if not agreement:
            raise AgencyAgreementNotExists

        return agreement
