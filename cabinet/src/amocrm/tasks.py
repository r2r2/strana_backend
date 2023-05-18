from asyncio import get_event_loop
from typing import Any

import tortoise
from common.backend.repos import (BackendAmocrmPipelinesRepo,
                                  BackendAmocrmStatusesRepo)
from config import celery, tortoise_config

from .repos import AmocrmPipelineRepo, AmocrmStatusRepo
from .services import ImportAmocrmService


@celery.app.task
def import_amocrm_periodic() -> None:
    """
    Переодический импорт AMOCRM из БД
    """
    resources: dict[str, Any] = dict(
        orm_class=tortoise.Tortoise, orm_config=tortoise_config,
        backend_pipelines_repo=BackendAmocrmPipelinesRepo, backend_statuses_repo=BackendAmocrmStatusesRepo,
        pipelines_repo=AmocrmPipelineRepo, statuses_repo=AmocrmStatusRepo,
    )
    import_cities_service = ImportAmocrmService(**resources)
    loop: Any = get_event_loop()
    loop.run_until_complete(celery.sentry_catch(celery.init_orm(import_cities_service))())
