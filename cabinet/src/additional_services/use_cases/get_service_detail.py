from tortoise.queryset import QuerySet

from ..entities import BaseAdditionalServiceCase
from ..exceptions import AdditionalServiceNotFoundError
from ..repos import (
    AdditionalServiceConditionStepRepo as StepRepo,
    AdditionalServiceRepo as ServiceRepo,
    AdditionalService as Service,
)


class ServiceDetailCase(BaseAdditionalServiceCase):
    """
    Кейс получения деталки услуги
    """

    def __init__(
        self,
        service_repo: type[ServiceRepo],
        step_repo: type[StepRepo],
    ) -> None:
        self.service_repo: ServiceRepo = service_repo()
        self.step_repo: StepRepo = step_repo()

    async def __call__(self, service_id: int) -> Service:
        active_filters: dict = dict(active=True)
        steps_qs: QuerySet = self.step_repo.list(
            filters=active_filters, ordering="priority"
        )
        active_filters.update(id=service_id)
        service: Service = await self.service_repo.retrieve(
            filters=active_filters,
            prefetch_fields=[
                dict(
                    relation="condition__condition_steps",
                    queryset=steps_qs,
                    to_attr="steps",
                )
            ],
        )
        if not service:
            raise AdditionalServiceNotFoundError
        return service
