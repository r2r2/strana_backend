import asyncio

import tortoise
from typing import Any

from common import amocrm
from common.celery.utils import redis_lock
from config import celery, tortoise_config
from common.amocrm import services
from common.amocrm.repos import AmoStatusesRepo, AmoPipelinesRepo


@celery.app.task
def update_amocrm_statuses_periodic():
    lock_id = "periodic_cache_update_amocrm_statuses_periodic"
    can_launch = redis_lock(lock_id)
    if not can_launch:
        return

    resources: dict[str:Any] = dict(
        amocrm_class=amocrm.AmoCRM,
        orm_class=tortoise.Tortoise,
        orm_config=tortoise_config,
        pipelines_repo=AmoPipelinesRepo,
        statuses_repo=AmoStatusesRepo
    )
    service: services.AmoUpdateStatusesService = services.AmoUpdateStatusesService(**resources)
    loop = asyncio.get_event_loop()
    loop.run_until_complete(celery.sentry_catch(celery.init_orm(service))())


@celery.app.task
def bind_contact_to_company(agent_amocrm_id: int, agency_amocrm_id: int):
    resources: dict[str:Any] = dict(
        amocrm_class=amocrm.AmoCRM,
        orm_class=tortoise.Tortoise,
        orm_config=tortoise_config,
    )
    service: services.BindContactCompanyService = services.BindContactCompanyService(**resources)
    loop = asyncio.get_event_loop()
    loop.run_until_complete(celery.sentry_catch(celery.init_orm(service))(
        agency_amocrm_id=agency_amocrm_id, agent_amocrm_id=agent_amocrm_id))
