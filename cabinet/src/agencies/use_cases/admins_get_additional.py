from typing import Any, Type

from src.agreements.repos import (AgencyAdditionalAgreement,
                                  AgencyAdditionalAgreementRepo)

from ..entities import BaseAgencyCase
from ..exceptions import AdditionalAgreementNotExists


class AdminAdditionalAgreementCase(BaseAgencyCase):
    """
    Получение дополнительного соглашения
    """

    def __init__(self,  additional_agreement_repo: Type[AgencyAdditionalAgreementRepo]):
        self.additional_agreement_repo: AgencyAdditionalAgreementRepo = additional_agreement_repo()

    async def __call__(self, additional_id: int) -> AgencyAdditionalAgreement:
        filters: dict[str, Any] = dict(id=additional_id)
        select_related = ["status", "agency"]
        additional_agreement: AgencyAdditionalAgreement = await self.additional_agreement_repo.retrieve(
            filters=filters,
            related_fields=select_related,
        )
        if not additional_agreement:
            raise AdditionalAgreementNotExists

        return additional_agreement
