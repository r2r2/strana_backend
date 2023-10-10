from asyncio import get_event_loop
from typing import Any

from common.backend import repos as backend_repos
from common.celery.utils import redis_lock
from config import celery, tortoise_config
from src.buildings import repos as buildings_repos
from src.properties.services import (ImportBuildingBookingTypesService, ImportPropertyService,
                                     ImportPropertyServiceFactory)
from tortoise import Tortoise


@celery.app.task
def import_property_task(property_id: int) -> None:
    # unused
    """
    Импорт объектов недвижимости из бекенда
    """
    import_property: ImportPropertyService = ImportPropertyServiceFactory.create(
        orm_class=Tortoise,
        orm_config=tortoise_config
    )
    loop: Any = get_event_loop()
    loop.run_until_complete(
        celery.sentry_catch(celery.init_orm(import_property))(property_id=property_id)
    )


@celery.app.task
def import_properties_task_periodic() -> None:
    """
    Периодический импорт объектов недвижимости из бекенда
    """
    lock_id = "periodic_cache_import_properties_task_periodic"
    can_launch = redis_lock(lock_id)
    if not can_launch:
        return

    import_building_booking_types_service: ImportBuildingBookingTypesService = ImportBuildingBookingTypesService(
            backend_building_booking_type_repo=backend_repos.BackendBuildingBookingTypesRepo,
            building_booking_type_repo=buildings_repos.BuildingBookingTypeRepo,
        )
    import_property: ImportPropertyService = ImportPropertyServiceFactory.create(
        orm_class=Tortoise,
        orm_config=tortoise_config,
        import_building_booking_types_service=import_building_booking_types_service,
    )
    loop: Any = get_event_loop()
    loop.run_until_complete(celery.sentry_catch(import_property.periodic)())
