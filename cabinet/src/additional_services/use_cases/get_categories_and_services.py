from tortoise.queryset import QuerySet

from ..entities import BaseAdditionalServiceCase
from ..repos import (
    AdditionalServiceCategoryRepo as CategoryRepo,
    AdditionalServiceCategory as Category,
    AdditionalServiceRepo as ServiceRepo,
)


class CategoriesAndServicesListCase(BaseAdditionalServiceCase):
    """
    Кейс получения списка категорий и услуг
    """

    def __init__(
        self,
        category_repo: type[CategoryRepo],
        service_repo: type[ServiceRepo],
    ) -> None:
        self.category_repo: CategoryRepo = category_repo()
        self.service_repo: ServiceRepo = service_repo()

    async def __call__(self) -> list[Category]:
        active_filters: dict = dict(active=True)
        services_qs: QuerySet = self.service_repo.list(
            filters=active_filters, ordering="priority"
        )
        categories: list[Category] = await self.category_repo.list(
            filters=active_filters,
            prefetch_fields=[
                dict(
                    relation="service_categories",
                    queryset=services_qs,
                    to_attr="services",
                )
            ],
            ordering="priority",
        )
        return categories
