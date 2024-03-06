from src.amocrm.repos import AmocrmStatusRepo, AmocrmPipelineRepo, AmocrmStatus
from src.mortgage.entities import BaseMortgageCase


class GetAmoStatusesPipelinesCase(BaseMortgageCase):
    def __init__(
        self,
        amocrm_status_repo: type[AmocrmStatusRepo],
        amocrm_pipeline_repo: type[AmocrmPipelineRepo],
    ):
        self.amocrm_status_repo: AmocrmStatusRepo = amocrm_status_repo()
        self.amocrm_pipeline_repo: AmocrmPipelineRepo = amocrm_pipeline_repo()

    async def __call__(self) -> dict[str, list[dict]]:
        amo_statuses: list[dict] = await self.amocrm_status_repo.list().values("id", "name", "pipeline_id")
        pipelines: list[dict] = await self.amocrm_pipeline_repo.list().values("id", "name")

        return dict(
            statuses=amo_statuses,
            pipelines=pipelines,
        )
