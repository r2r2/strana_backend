from asyncio import get_event_loop
from typing import Any

import tortoise
from common.backend.repos import BackendCitiesRepo
from config import celery, tortoise_config

from .repos import CityRepo
from .services import ImportCitiesService


@celery.app.task
def import_cities_periodic() -> None:
    """
    Переодический импорт городов из БД
    """
    resources: dict[str, Any] = dict(
        orm_class=tortoise.Tortoise, orm_config=tortoise_config,
        backend_city_repo=BackendCitiesRepo, city_repo=CityRepo
    )
    import_cities_service = ImportCitiesService(**resources)
    loop: Any = get_event_loop()
    loop.run_until_complete(celery.sentry_catch(celery.init_orm(import_cities_service))())
