from ..entities import BaseAdditionalServiceCase
from ..repos import (
    AdditionalServiceCategoryRepo as CategoryRepo,
    AdditionalServiceCategory as Category,
)


class GetFacetCase(BaseAdditionalServiceCase):
    """
    Кейс получения фасетов
    """

    def __init__(
        self,
        category_repo: type[CategoryRepo],
    ) -> None:
        self.category_repo: CategoryRepo = category_repo()

    async def __call__(self, user_id: int) -> dict:
        filters: dict = dict(service_category__service_ticket__user_id=user_id)
        category_facets: list[dict] = [dict(id=None, title="Все")]
        category_db_facets: list[Category] = await self.category_repo.list(
            filters=filters, distinct=True
        )
        category_facets.extend(category_db_facets)
        facets: dict = dict(categories=category_facets)
        return facets
