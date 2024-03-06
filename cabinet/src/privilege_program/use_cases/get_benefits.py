from ..entities import BasePrivilegeServiceCase
from ..repos import PrivilegeBenefitRepo, PrivilegeBenefit


class BenefitListCase(BasePrivilegeServiceCase):
    """
    Кейс получения преимуществ
    """

    def __init__(
        self,
        benefit_repo: type[PrivilegeBenefitRepo],
    ) -> None:
        self.benefit_repo: PrivilegeBenefitRepo = benefit_repo()

    async def __call__(self) -> list[PrivilegeBenefit]:
        active_filters: dict = dict(is_active=True)
        benefits: list[PrivilegeBenefit] = await self.benefit_repo.list(filters=active_filters, ordering="priority")
        return benefits
