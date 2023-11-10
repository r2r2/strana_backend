from typing import Any, Optional, Type, Union

from src.agreements.repos import AgencyActRepo
from tortoise.queryset import QuerySet

from ..entities import BaseAgencyCase
from ..exceptions import AgencyNotFoundError
from ..repos import Agency, AgencyRepo
from ..types import AgencyPagination, AgencyUserRepo


class ListActsCase(BaseAgencyCase):
    """
    Получение актов
    """

    def __init__(
        self,
        act_repo: Type[AgencyActRepo],
        agency_repo: Type[AgencyRepo],
        user_repo: Type[AgencyUserRepo],
    ):
        self.act_repo: AgencyActRepo = act_repo()
        self.agency_repo: AgencyRepo = agency_repo()
        self.user_repo: AgencyUserRepo = user_repo()

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
            q_filters: list[Any] = [self.act_repo.q_builder(or_filters=search[0])]
        else:
            q_base: Any = self.act_repo.q_builder()
            for s in search:
                q_base |= self.act_repo.q_builder(and_filters=s)
            q_filters: list[Any] = [q_base]

        if repres_id:
            agency: Agency = await self.agency_repo.retrieve(filters=dict(maintainer=repres_id))
            if not agency:
                raise AgencyNotFoundError
            additional_filters = dict(agency_id=agency.id)
        else:
            additional_filters = dict(booking__agent_id=agent_id)

        init_filters.update(additional_filters)
        select_related = ["agency", "status", "booking__user", "booking__agent"]
        annotations = dict(
            user=self.user_repo.a_builder.build_f("agencies_act__booking__user"),
            agent=self.user_repo.a_builder.build_f("agencies_act__booking__agent"),
        )
        agency_acts_query: QuerySet = self.act_repo.list(
            ordering=ordering,
            q_filters=q_filters,
            filters=init_filters,
            related_fields=select_related,
            annotations=annotations,
            start=pagination.start,
            end=pagination.end,
        )

        count: int = await self.act_repo.count(
            q_filters=q_filters,
            filters=init_filters,
        )
        agency_acts = await agency_acts_query

        data: dict[str, Any] = dict(count=count, result=agency_acts, page_info=pagination(count=count))
        return data
