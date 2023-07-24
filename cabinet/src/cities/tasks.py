from asyncio import get_event_loop
from typing import Any

import tortoise

from common.backend.repos import BackendCitiesRepo
from common.portal.portal import PortalAPI
from common.requests import GraphQLRequest
from config import celery, tortoise_config, backend_config
from src.cities.repos.city import CityRepo
from .services import ImportCitiesService
from .services.update_cities_data import UpdateCitiesService


@celery.app.task
def periodic_cities_update_task() -> None:
    """
    Обновление списка городов
    """
    resources = dict(orm_class=tortoise.Tortoise, orm_config=tortoise_config,
                     cities_repo=CityRepo,
                     portal_class=PortalAPI(request_class=GraphQLRequest, portal_config=backend_config))
    update_cities: UpdateCitiesService = UpdateCitiesService(**resources)
    loop = get_event_loop()
    loop.run_until_complete(celery.init_orm(update_cities)())
