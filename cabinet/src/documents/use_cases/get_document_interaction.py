from typing import Any, Type, Optional, Union
from ..entities import BaseDocumentCase
from ..repos import InteractionDocument, InteractionDocumentRepo

from ..exceptions import InteractionDocumentNotFoundError
from ..types import InteractionDocumentsPagination
from tortoise.queryset import QuerySet


class GetInteractionDocumentCase(BaseDocumentCase):
    """
    Получение взаимодействий.
    """

    def __init__(self, interaction_repo: Type[InteractionDocumentRepo]) -> None:
        self.interaction_repo: InteractionDocumentRepo = interaction_repo()

    async def __call__(
        self,
        pagination: InteractionDocumentsPagination,
    ) -> dict[str, Any]:
        interactions: list[InteractionDocument] = await self.interaction_repo.list(
            start=pagination.start,
            end=pagination.end,
        )
        if not interactions:
            raise InteractionDocumentNotFoundError

        count: int = await self.interaction_repo.count()

        data: dict[str, Any] = dict(
            count=count,
            result=interactions,
            page_info=pagination(count=count),
        )

        return data
