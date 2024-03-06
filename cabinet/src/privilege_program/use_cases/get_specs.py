from ..entities import BasePrivilegeServiceCase
from ..repos import (
    PrivilegeCategoryRepo as CategoryRepo,
    PrivilegeCategory as Category,
)


class GetSpecCase(BasePrivilegeServiceCase):
    """
    Кейс получения спеков
    """

    def __init__(
        self,
        category_repo: type[CategoryRepo],
    ) -> None:
        self.category_repo: CategoryRepo = category_repo()

    async def __call__(self, city: str | None) -> dict:
        active_filters: dict = dict(is_active=True, )
        category_specs: list[dict] = [dict(slug="all", title="Все")]
        category_db_specs: list[Category] = await self.category_repo.list(
            filters=active_filters, ordering="filter_priority"
        )
        filtered_categories = []
        for category in category_db_specs:
            if (city in [city.slug for city in await category.cities]) or city is None:
                filtered_categories.append(category)
        category_specs.extend([dict(slug=category.slug, title=category.title) for category in filtered_categories])
        specs: dict = dict(categories=category_specs)
        return specs
