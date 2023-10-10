from typing import Any

from common import dependencies
from fastapi import APIRouter, Depends, status
from src.properties import repos
from src.properties import services as property_services
from src.properties import use_cases
from src.users import constants as users_constants
from src.users import repos as users_repos

from ..models import ViewedPropertyListResponse, ViewedPropertyResponse

router = APIRouter(prefix="/favourites", tags=["favourites"])


@router.post("/latest", status_code=status.HTTP_201_CREATED, response_model=list[ViewedPropertyResponse])
async def add_viewed_properties_view(
    viewed_global_ids: list[str],
    user_id: int = Depends(dependencies.CurrentUserId(user_type=users_constants.UserType.CLIENT)),
):
    """
    Добавление объектов недвижимости в просмотренное
    """
    import_property_service: property_services.ImportPropertyService = \
        property_services.ImportPropertyServiceFactory.create()
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
