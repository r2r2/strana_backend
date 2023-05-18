from typing import Type, Any, Union

from tortoise.queryset import QuerySet

from src.agencies.types import AgencyPagination, AgencyUserRepo
from src.agreements.entities import BaseAgreementCase
from src.agreements.repos import AgencyActRepo


class AdminListActsCase(BaseAgreementCase):
    """
    Получение актов админом
    """

    def __init__(
            self,
            act_repo: Type[AgencyActRepo],
            user_repo: Type[AgencyUserRepo]
    ):
        self.act_repo: AgencyActRepo = act_repo()
        self.user_repo: AgencyUserRepo = user_repo()

    async def __call__(
            self,
            pagination: AgencyPagination,
            init_filters: dict[str, Any],
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

        related_fields = ["agency", "status", "booking__user", "booking__agent"]
        annotations = dict(
            user=self.user_repo.a_builder.build_f("agencies_act__booking__user"),
            agent=self.user_repo.a_builder.build_f("agencies_act__booking__agent"),
        )
        acts_queryset: QuerySet = self.act_repo.list(
            related_fields=related_fields,
            ordering=ordering,
            filters=init_filters,
            q_filters=q_filters,
            annotations=annotations,
            start=pagination.start,
            end=pagination.end,
        )

        acts_query_count: QuerySet = self.act_repo.list(
            q_filters=q_filters,
            filters=init_filters,
        )
        count: int = await acts_query_count.count()
        acts = await acts_queryset

        return dict(
            result=acts,
            count=count,
            page_info=pagination(count=count)
        )
