from asyncio import get_event_loop
from typing import Any

from common import amocrm, redis
from config import celery, redis_config, tortoise_config
from src.agencies import repos as agencies_repos
from src.agencies import services, loggers
from src.agents import repos as agents_repos
from src.booking import repos as booking_repos
from src.users import constants as users_constants
from src.users import repos as users_repos
from tortoise import Tortoise


@celery.app.task
def check_organization_task_periodic() -> None:
    """
    Периодическая проверка агентства
    """
    resources: dict[str, Any] = dict(
        redis=redis.broker,
        orm_class=Tortoise,
        redis_config=redis_config,
        orm_config=tortoise_config,
        amocrm_class=amocrm.AmoCRM,
        check_repo=users_repos.CheckRepo,
        agent_repo=agents_repos.AgentRepo,
        user_types=users_constants.UserType,
        agency_repo=agencies_repos.AgencyRepo,
        booking_repo=booking_repos.BookingRepo,
    )
    check_organization: services.CheckOrganizationService = services.CheckOrganizationService(
        **resources
    )
    loop: Any = get_event_loop()
    loop.run_until_complete(celery.sentry_catch(celery.init_orm(check_organization))())


@celery.app.task
def create_organization_task(agency_id: int):
    """
    Create company for amocrm. Required agency_id
    """

    resources: dict[str, Any] = dict(
        orm_class=Tortoise,
        orm_config=tortoise_config,
        amocrm_class=amocrm.AmoCRM,
        agency_repo=agencies_repos.AgencyRepo,
    )
    create_organization_service = services.CreateOrganizationService(**resources)
    loop: Any = get_event_loop()
    loop.run_until_complete(
        celery.sentry_catch(celery.init_orm(create_organization_service))(agency_id=agency_id)
    )


@celery.app.task
def update_organization_task(agency_id: int):
    """
    Update company for amocrm, Required agency_id
    """
    resources: dict[str, Any] = dict(
        amocrm_class=amocrm.AmoCRM,
        agency_repo=agencies_repos.AgencyRepo,
        orm_class=Tortoise,
        orm_config=tortoise_config,
    )
    create_organization_service = services.UpdateOrganizationService(**resources)
    loop: Any = get_event_loop()
    loop.run_until_complete(
        celery.sentry_catch(celery.init_orm(create_organization_service))(agency_id=agency_id)
    )


@celery.app.task
def create_agency_log_task(log_data: dict[str, Any]) -> None:
    """
    Создание лога агентства
    """
    resources: dict[str, Any] = dict(
        orm_class=Tortoise, orm_config=tortoise_config, booking_repo=agencies_repos.AgencyLogRepo
    )
    create_log: loggers.CreateAgencyLogger = loggers.CreateAgencyLogger(**resources)
    loop: Any = get_event_loop()
    loop.run_until_complete(celery.sentry_catch(celery.init_orm(create_log))(log_data=log_data))


@celery.app.task
async def create_agency_log_task(log_data: dict[str, Any]) -> None:
    """
    Создание лога агентства
    """
    resources: dict[str, Any] = dict(
        orm_class=Tortoise, orm_config=tortoise_config, agency_log_repo=agencies_repos.AgencyLogRepo
    )
    create_log: loggers.CreateAgencyLogger = loggers.CreateAgencyLogger(**resources)

    await create_log(log_data=log_data)
