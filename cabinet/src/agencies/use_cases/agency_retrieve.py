from typing import Type, Any, Optional

from ..exceptions import AgencyNotFoundError, AgencyNotApprovedError
from ..repos import AgencyRepo, Agency
from ..entities import BaseAgencyCase


class AgencyRetrieveCase(BaseAgencyCase):
    """
    Получение агенства
    """

    def __init__(self, agency_repo: Type[AgencyRepo]) -> None:
        self.agency_repo: AgencyRepo = agency_repo()

    async def __call__(self, agency_inn: str) -> Agency:
        filters: dict[str, Any] = dict(inn=agency_inn)
        agency: Optional[Agency] = await self.agency_repo.retrieve(filters=filters, related_fields=["city"])
        if not agency:
            raise AgencyNotFoundError
        if not agency.is_approved:
            raise AgencyNotApprovedError
        return agency
