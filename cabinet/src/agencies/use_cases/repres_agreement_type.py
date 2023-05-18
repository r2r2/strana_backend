from typing import Type

from src.agreements.repos import AgreementType, AgreementTypeRepo

from ..entities import BaseAgencyCase


class RepresAgreementTypeCase(BaseAgencyCase):
    """
    Получение типов договоров
    """

    def __init__(self, agreement_type_repo: Type[AgreementTypeRepo]):
        self.agreement_type_repo: AgreementTypeRepo = agreement_type_repo()

    async def __call__(self) -> list[AgreementType]:
        return await self.agreement_type_repo.list()
