from typing import Any

from fastapi import status, APIRouter, Depends

from common import dependencies, utils
from common.backend import repos as backend_repos
from src.properties import repos
from src.properties import use_cases
from src.properties import services as property_services
from src.users import constants as users_constants
from src.users import repos as users_repos
from src.projects import repos as projects_repos
from src.buildings import repos as buildings_repos
from src.floors import repos as floors_repos
from ..models import ViewedPropertyResponse, ViewedPropertyListResponse

router = APIRouter(prefix="/favourites", tags=["favourites"])


@router.post("/latest", status_code=status.HTTP_201_CREATED, response_model=list[ViewedPropertyResponse])
async def add_viewed_properties_view(
    viewed_global_ids: list[str],
    user_id: int = Depends(dependencies.CurrentUserId(user_type=users_constants.UserType.CLIENT)),
):
    """
    Добавление объектов недвижимости в просмотренное
    """
    import_property_service: property_services.ImportPropertyService = property_services.ImportPropertyService(
        floor_repo=floors_repos.FloorRepo,
        global_id_decoder=utils.from_global_id,
        global_id_encoder=utils.to_global_id,
        project_repo=projects_repos.ProjectRepo,
        building_repo=buildings_repos.BuildingRepo,
        feature_repo=repos.FeatureRepo,
        property_repo=repos.PropertyRepo,
        building_booking_type_repo=buildings_repos.BuildingBookingTypeRepo,
        backend_building_booking_type_repo=backend_repos.BackendBuildingBookingTypesRepo,
        backend_properties_repo=backend_repos.BackendPropertiesRepo,
        backend_floors_repo=backend_repos.BackendFloorsRepo,
        backend_sections_repo=backend_repos.BackendSectionsRepo,
        backend_special_offers_repo=backend_repos.BackendSpecialOfferRepo,
    )
    resources: dict[str, Any] = dict(
        property_repo=repos.PropertyRepo,
        viewed_property_repo=users_repos.UserViewedPropertyRepo,
        import_property_service=import_property_service,
    )
    add_viewed_properties: use_cases.AddViewedPropertiesCase = use_cases.AddViewedPropertiesCase(**resources)
    return await add_viewed_properties(user_id=user_id, viewed_global_ids=viewed_global_ids)


@router.get("/latest", status_code=status.HTTP_200_OK, response_model=list[ViewedPropertyListResponse])
async def get_viewed_properties_list_view(
    user_id: int = Depends(dependencies.CurrentUserId(user_type=users_constants.UserType.CLIENT)),
):
    """
    Получение просмотренных объектов недвижимости
    """
    resources: dict[str, Any] = dict(
        property_repo=repos.PropertyRepo,
        feature_repo=repos.FeatureRepo,
    )
    add_viewed_properties: use_cases.GetViewedPropertiesCase = use_cases.GetViewedPropertiesCase(**resources)
    return await add_viewed_properties(user_id=user_id)


@router.get("/latest/ids", status_code=status.HTTP_200_OK)
async def get_viewed_properties_list_ids_view(
    user_id: int = Depends(dependencies.CurrentUserId(user_type=users_constants.UserType.CLIENT)),
):
    """
    Получение списка global_id просмотренных объектов недвижимости
    """
    resources: dict[str, Any] = dict(
        property_repo=repos.PropertyRepo,
    )
    get_viewed_properties_ids: use_cases.GetViewedPropertiesIdsCase = use_cases.GetViewedPropertiesIdsCase(**resources)
    return await get_viewed_properties_ids(user_id=user_id)
