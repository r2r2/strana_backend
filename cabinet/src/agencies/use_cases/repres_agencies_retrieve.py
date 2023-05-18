from typing import Optional, Type

from src.users.repos import User

from ..entities import BaseAgencyCase
from ..exceptions import AgencyNotFoundError
from ..repos import Agency, AgencyRepo
from ..types import AgencyUserRepo


class AgenciesRetrieveCase(BaseAgencyCase):
    """
    Получение данных агенства представителем
    """

    def __init__(
        self,
        agency_repo: Type[AgencyRepo],
        user_repo: Type[AgencyUserRepo],
    ) -> None:
        self.agency_repo: AgencyRepo = agency_repo()
        self.user_repo: AgencyUserRepo = user_repo()

    async def __call__(self, repres_id: Optional[int] = None, agent_id: Optional[int] = None) -> Agency:
        if repres_id:
            agency: Agency = await self.agency_repo.retrieve(filters=dict(maintainer=repres_id))
        else:
            agent: User = await self.user_repo.retrieve(filters=dict(id=agent_id), related_fields=["agency"])
            agency: Agency = await agent.agency
        if not agency:
            raise AgencyNotFoundError
        return agency
