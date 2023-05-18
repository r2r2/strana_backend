from copy import copy
from typing import Optional, Type

import tortoise
from common.backend.models import AmocrmPipelines, AmocrmStatus
from common.backend.repos import (BackendAmocrmPipelinesRepo,
                                  BackendAmocrmStatusesRepo)

from ..entities import BaseAmocrmService
from ..repos import AmocrmPipeline, AmocrmPipelineRepo, AmocrmStatusRepo


class ImportAmocrmService(BaseAmocrmService):
    """
    Импорт городов из БД
    """

    def __init__(
        self,
        orm_class: Optional[Type[tortoise.Tortoise]],
        orm_config: Optional[dict],
        backend_pipelines_repo: Type[BackendAmocrmPipelinesRepo],
        backend_statuses_repo: Type[BackendAmocrmStatusesRepo],
        pipelines_repo: Type[AmocrmPipelineRepo],
        statuses_repo: Type[AmocrmStatusRepo]
    ):
        self.backend_pipelines_repo = backend_pipelines_repo()
        self.backend_statuses_repo = backend_statuses_repo()
        self.pipelines_repo = pipelines_repo()
        self.statuses_repo = statuses_repo()
        self.orm_class = orm_class
        self.orm_config = copy(orm_config)
        if self.orm_config:
            self.orm_config.pop("generate_schemas", None)

    async def __call__(self):
        filters = dict(is_archive=False)
        backend_pipelines: list[AmocrmPipelines] = await self.backend_pipelines_repo.list(filters=filters)
        pipelines: dict[int, AmocrmPipeline] = {}
        for backend_pipeline in backend_pipelines:
            filters = dict(id=backend_pipeline.id)
            pipeline_data = dict(name=backend_pipeline.name, sort=backend_pipeline.sort)
            pipeline = await self.pipelines_repo.update_or_create(filters=filters, data=pipeline_data)
            pipelines[pipeline.id] = pipeline

        backend_statuses: list[AmocrmStatus] = await self.backend_statuses_repo.list()
        for backend_status in backend_statuses:
            filters: dict = dict(id=backend_status.id)
            status_data: dict = dict(
                name=backend_status.name,
                pipeline=pipelines[backend_status.pipeline_id],
                sort=backend_status.sort
            )
            await self.statuses_repo.update_or_create(filters=filters, data=status_data)
