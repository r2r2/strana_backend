from asyncio import get_event_loop
from typing import Any

from common import utils
from common.backend import repos as backend_repos
from config import celery, tortoise_config
from src.buildings import repos as buildings_repos
from src.floors import repos as floors_repos
from src.projects import repos as projects_repos
from src.properties import repos as properties_repos
from src.properties.services import (ImportBuildingBookingTypesService,
                                     ImportPropertyService)
from tortoise import Tortoise


@celery.app.task
def import_property_task(property_id: int) -> None:
    # unused
    """
    Импорт объектов недвижимости из бекенда
    """
    import_property: ImportPropertyService = ImportPropertyService(
        orm_class=Tortoise,
        orm_config=tortoise_config,
        floor_repo=floors_repos.FloorRepo,
        global_id_decoder=utils.from_global_id,
        global_id_encoder=utils.to_global_id,
        project_repo=projects_repos.ProjectRepo,
        building_repo=buildings_repos.BuildingRepo,
        property_repo=properties_repos.PropertyRepo,
        building_booking_type_repo=buildings_repos.BuildingBookingTypeRepo,
        backend_building_booking_type_repo=backend_repos.BackendBuildingBookingTypesRepo,
        backend_properties_repo=backend_repos.BackendPropertiesRepo,
        backend_floors_repo=backend_repos.BackendFloorsRepo,
        backend_sections_repo=backend_repos.BackendSectionsRepo,
    )
    loop: Any = get_event_loop()
    loop.run_until_complete(
        celery.sentry_catch(celery.init_orm(import_property))(property_id=property_id)
    )


@celery.app.task
def import_properties_task_periodic() -> None:
    """
    Переодический импорт объектов недвижимости из бекенда
    """
    import_building_booking_types_service: ImportBuildingBookingTypesService = ImportBuildingBookingTypesService(
            backend_building_booking_type_repo=backend_repos.BackendBuildingBookingTypesRepo,
            building_booking_type_repo=buildings_repos.BuildingBookingTypeRepo,
        )
    import_property: ImportPropertyService = ImportPropertyService(
        orm_class=Tortoise,
        orm_config=tortoise_config,
        floor_repo=floors_repos.FloorRepo,
        global_id_decoder=utils.from_global_id,
        global_id_encoder=utils.to_global_id,
        project_repo=projects_repos.ProjectRepo,
        building_repo=buildings_repos.BuildingRepo,
        property_repo=properties_repos.PropertyRepo,
        building_booking_type_repo=buildings_repos.BuildingBookingTypeRepo,
        backend_building_booking_type_repo=backend_repos.BackendBuildingBookingTypesRepo,
        backend_properties_repo=backend_repos.BackendPropertiesRepo,
        backend_floors_repo=backend_repos.BackendFloorsRepo,
        backend_sections_repo=backend_repos.BackendSectionsRepo,
        import_building_booking_types_service=import_building_booking_types_service,
    )
    loop: Any = get_event_loop()
    loop.run_until_complete(celery.sentry_catch(import_property.periodic)())
