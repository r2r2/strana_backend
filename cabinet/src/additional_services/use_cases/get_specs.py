from ..entities import BaseAdditionalServiceCase
from ..repos import (
    AdditionalServiceCategoryRepo as CategoryRepo,
    AdditionalServiceCategory as Category,
)


class GetSpecCase(BaseAdditionalServiceCase):
    """
    Кейс получения спеков
    """

    def __init__(
        self,
        category_repo: type[CategoryRepo],
    ) -> None:
        self.category_repo: CategoryRepo = category_repo()

    async def __call__(self) -> dict:
        active_filters: dict = dict(active=True)
        category_specs: list[dict] = [dict(id=None, title="Все")]
        category_db_specs: list[Category] = await self.category_repo.list(
            filters=active_filters, ordering="priority"
        )
        category_specs.extend(category_db_specs)
        specs: dict = dict(categories=category_specs)
        return specs
