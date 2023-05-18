from typing import Any, Optional, Type, Union

from src.agreements.repos import AgencyAdditionalAgreementRepo
from tortoise.queryset import QuerySet

from ..entities import BaseAgencyCase
from ..types import AgencyPagination


class ListAdminAdditionalAgreementsCase(BaseAgencyCase):
    """
    Получение дополнительных соглашений
    """

    def __init__(
        self,
        additional_agreement_repo: Type[AgencyAdditionalAgreementRepo],
    ):
        self.additional_agreement_repo = additional_agreement_repo()

    async def __call__(
        self,
        pagination: AgencyPagination,
        init_filters: dict[str, Any],
    ) -> dict[str, Any]:

        ordering: Union[str, None] = init_filters.pop("ordering", "-id")
        search: list[list[dict[str, Any]]] = init_filters.pop("search", [])

        if len(search) == 1:
            q_filters: list[Any] = [self.additional_agreement_repo.q_builder(or_filters=search[0])]
        else:
            q_base: Any = self.additional_agreement_repo.q_builder()
            for s in search:
                q_base |= self.additional_agreement_repo.q_builder(and_filters=s)
            q_filters: list[Any] = [q_base]

        select_related = ["status", "agency"]
        additional_agreements = await self.additional_agreement_repo.list(
            start=pagination.start,
            end=pagination.end,
            ordering=ordering,
            q_filters=q_filters,
            related_fields=select_related,
        )
        counted = await self.additional_agreement_repo.list(
            q_filters=q_filters,
        ).count()

        data: dict[str, Any] = dict(count=counted, result=additional_agreements, page_info=pagination(count=counted))

        return data
