from asyncio import get_event_loop

import tortoise

from common.portal.portal import PortalAPI
from common.requests import GraphQLRequest
from common.celery.utils import redis_lock
from config import celery, tortoise_config, backend_config
from src.cities.repos.city import CityRepo
from .services.update_cities_data import UpdateCitiesService


@celery.app.task
def periodic_cities_update_task() -> None:
    """
    Обновление списка городов
    """
    lock_id = "periodic_cache_periodic_cities_update_task"
    can_launch = redis_lock(lock_id)
    if not can_launch:
        return

    resources = dict(orm_class=tortoise.Tortoise, orm_config=tortoise_config,
                     cities_repo=CityRepo,
                     portal_class=PortalAPI(request_class=GraphQLRequest, portal_config=backend_config))
    update_cities: UpdateCitiesService = UpdateCitiesService(**resources)
    loop = get_event_loop()
    loop.run_until_complete(celery.init_orm(update_cities)())
