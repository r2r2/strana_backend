from typing import Any, Optional, Type

from src.agencies.exceptions import AgencyActNotExists
from src.agreements.repos import AgencyAct, AgencyActRepo
from src.users.repos import User

from ..entities import BaseAgencyCase
from ..types import AgencyUserRepo


class SingleActCase(BaseAgencyCase):
    """
    Получение договора
    """

    def __init__(
        self, act_repo: Type[AgencyActRepo],
        user_repo: Type[AgencyUserRepo],
        agent_repo: Type[AgencyUserRepo],
    ):
        self.act_repo: AgencyActRepo = act_repo()
        self.user_repo: AgencyUserRepo = user_repo()
        self.agent_repo: AgencyUserRepo = agent_repo()

    async def __call__(
        self,
        act_id: int,
        agent_id: Optional[int] = None,
        repres_id: Optional[int] = None
    ) -> AgencyAct:
        filters: dict[str, Any] = dict(id=act_id)
        if agent_id:
            filters.update(booking__agent_id=agent_id)
        elif repres_id:
            repres: User = await self.agent_repo.retrieve(filters=dict(id=repres_id), related_fields=["agency"])
            filters.update(agency_id=repres.agency.id)

        select_related = ["status", "agency", "booking__user", "booking__agent"]
        annotations = dict(
            user=self.user_repo.a_builder.build_f("agencies_act__booking__user"),
            agent=self.user_repo.a_builder.build_f("agencies_act__booking__agent"),
        )

        agency_act: AgencyAct = await self.act_repo.retrieve(
            filters=filters,
            related_fields=select_related,
            annotations=annotations
        )
        if not agency_act:
            raise AgencyActNotExists

        return agency_act
