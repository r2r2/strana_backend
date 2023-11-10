from typing import Type, Any, Union

from tortoise.queryset import QuerySet

from src.agencies.types import AgencyPagination
from src.agreements.entities import BaseAgreementCase
from src.agreements.repos import AgencyAgreementRepo


class AdminListAgreementsCase(BaseAgreementCase):
    """
    Получение договоров админом
    """
    def __init__(self, agreements_repo: Type[AgencyAgreementRepo]):
        self.agreements_repo: AgencyAgreementRepo = agreements_repo()

    async def __call__(
            self,
            pagination: AgencyPagination,
            init_filters: dict[str, Any],
    ) -> dict[str, Any]:
        ordering: Union[str, None] = init_filters.pop("ordering", "-id")
        search: list[list[dict[str, Any]]] = init_filters.pop("search", [])
        if len(search) == 1:
            q_filters: list[Any] = [self.agreements_repo.q_builder(or_filters=search[0])]
        else:
            q_base: Any = self.agreements_repo.q_builder()
            for s in search:
                q_base |= self.agreements_repo.q_builder(and_filters=s)
            q_filters: list[Any] = [q_base]

        select_related = ["status", "agreement_type", "agency"]
        agreements_queryset: QuerySet = self.agreements_repo.list(
            related_fields=select_related,
            ordering=ordering,
            q_filters=q_filters,
            filters=init_filters,
            start=pagination.start,
            end=pagination.end,
        )

        count: int = await self.agreements_repo.count(
            q_filters=q_filters,
            filters=init_filters,
        )
        agreements = await agreements_queryset

        return dict(
            result=agreements,
            count=count,
            page_info=pagination(count=count)
        )
