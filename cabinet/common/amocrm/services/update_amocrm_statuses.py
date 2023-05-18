from copy import copy
from typing import Any, Optional, Type

import jmespath
import tortoise
from common.amocrm import AmoCRM
from common.amocrm.entities import BaseAmocrmService
from common.amocrm.models import PipelineDTO, StatusDTO
from common.amocrm.repos import AmoPipelinesRepo, AmoStatusesRepo


class AmoUpdateStatusesService(BaseAmocrmService):

    def __init__(
            self,
            amocrm_class: Type[AmoCRM],
            orm_class: Optional[Type[tortoise.Tortoise]],
            orm_config: Optional[dict],
            pipelines_repo: Type[AmoPipelinesRepo],
            statuses_repo: Type[AmoStatusesRepo]
    ):
        self.amocrm_class = amocrm_class
        self.pipelines_repo = pipelines_repo()
        self.statuses_repo = statuses_repo()
        self.orm_class = orm_class
        self.orm_config = copy(orm_config)
        if self.orm_config:
            self.orm_config.pop("generate_schemas", None)

    async def __call__(self, *args, **kwargs):
        pipelines_data: list[dict] = await self._get_pipelines_data()
        pipelines_list: list[PipelineDTO] = self._parse_pipelines(pipelines_data)
        statuses_list: list[StatusDTO] = self._parse_statuses(pipelines_data)

        await self._update_db_pipelines(pipelines_list)
        await self._update_db_statuses(statuses_list)

    async def _get_pipelines_data(self) -> list[Optional[dict[Any]]]:
        """get pipelines data"""
        async with await self.amocrm_class() as amocrm:
            return await amocrm.get_leads_pipelines()

    @staticmethod
    def _parse_pipelines(data: list[dict[Any]]) -> list[PipelineDTO]:
        """parse pipelines"""
        result = []
        for pipeline in data:
            result.append(PipelineDTO(**pipeline))
        return result

    @staticmethod
    def _parse_statuses(data: list[dict[Any]]) -> list[StatusDTO]:
        """parse statuses"""
        result = []
        for pipeline in data:
            statuses = jmespath.search('_embedded.statuses', pipeline) or []
            for status in statuses:
                result.append(StatusDTO(**status))
        return result

    async def _update_db_statuses(self, data: list[StatusDTO]):
        """update statuses"""
        for status in data:
            status_dict = status.dict()
            filters: dict = dict(id=status_dict.pop('id'))
            await self.statuses_repo.update_or_create(filters=filters, data=status_dict)
        # Закрепляем завершающие статусы за воронкой "Все воронки"
        data = dict(
            name="Успешно реализовано",
            pipeline_id=1,
            sort=10000,
        )
        filters = dict(id=142)
        await self.statuses_repo.update_or_create(filters=filters, data=data)
        data = dict(
            name="Закрыто и не реализовано",
            pipeline_id=1,
            sort=11000,
        )
        filters = dict(id=143)
        await self.statuses_repo.update_or_create(filters=filters, data=data)

    async def _update_db_pipelines(self, data: list[PipelineDTO]):
        """update pipelines"""
        for pipeline in data:
            pipeline_dict = pipeline.dict()
            filters: dict = dict(id=pipeline_dict.pop('id'))
            await self.pipelines_repo.update_or_create(filters=filters, data=pipeline_dict)
        # Создаем доплнительную воронку "Все вороноки"
        data = dict(
            name="Все воронки",
            is_archive=False,
            is_main=False,
        )
        filters = dict(id=1)
        await self.pipelines_repo.update_or_create(filters=filters, data=data)
