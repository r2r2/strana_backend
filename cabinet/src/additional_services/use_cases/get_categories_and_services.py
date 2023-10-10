from tortoise.queryset import QuerySet

from ..entities import BaseAdditionalServiceCase
from ..repos import (
    AdditionalServiceRepo as ServiceRepo,
    AdditionalServiceType as ServiceType,
    AdditionalServiceTypeRepo as ServiceTypeRepo,
)


class CategoriesAndServicesListCase(BaseAdditionalServiceCase):
    """
    Кейс получения списка категорий и услуг
    """

    def __init__(
        self,
        service_repo: type[ServiceRepo],
        service_type_repo: type[ServiceTypeRepo],
    ) -> None:
        self.service_repo: ServiceRepo = service_repo()
        self.service_type_repo: ServiceTypeRepo = service_type_repo()

    async def __call__(self, category_id: int | None) -> list[ServiceType]:
        active_filters: dict = dict(active=True)
        if category_id:
            active_filters.update(category_id=category_id)

        services_qs: QuerySet = self.service_repo.list(filters=active_filters)
        service_types: list[ServiceType] = await self.service_type_repo.list(
            prefetch_fields=[
                dict(
                    relation="services",
                    queryset=services_qs,
                    to_attr="results",
                )
            ],
        )
        return service_types
