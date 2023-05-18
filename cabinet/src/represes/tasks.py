from typing import Any
from asyncio import get_event_loop

from tortoise import Tortoise

from common import amocrm
from config import celery, tortoise_config

from src.represes import services as represes_services
from src.agencies import repos as agencies_repos
from src.represes import repos as represes_repos


@celery.app.task
def create_contact_task(repres_id: int) -> None:
    """
    Create REPRES contact in amocrm.
    """
    resources: dict[str, Any] = dict(
        orm_class=Tortoise,
        orm_config=tortoise_config,
        amocrm_class=amocrm.AmoCRM,
        repres_repo=represes_repos.RepresRepo,
        agency_repo=agencies_repos.AgencyRepo,
    )
    create_contact_service = represes_services.CreateContactService(**resources)
    loop: Any = get_event_loop()
    loop.run_until_complete(
        celery.sentry_catch(celery.init_orm(create_contact_service))(repres_id=repres_id)
    )
