from ..entities import BaseAdditionalServiceCase
from ..repos import (
    AdditionalServiceCategoryRepo as CategoryRepo,
    AdditionalServiceTypeRepo as ServiceTypeRepo,
)


class GetSpecCase(BaseAdditionalServiceCase):
    """
    Кейс получения спеков
    """

    def __init__(
        self,
        category_repo: type[CategoryRepo],
        service_type_repo: type[ServiceTypeRepo],
    ) -> None:
        self.category_repo: CategoryRepo = category_repo()
        self.service_type_repo: ServiceTypeRepo = service_type_repo()

    async def __call__(self) -> dict:
        active_filters: dict = dict(active=True)
        category_specs: list[dict] = await self.category_repo.list(
            filters=active_filters
        ).values("id", "title")
        service_specs: list[dict] = await self.service_type_repo.list().values(
            "id", "title"
        )
        specs: dict = dict(
            categories=category_specs,
            service_types=service_specs,
        )
        return specs
