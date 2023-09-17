from fastapi import APIRouter, status, Path

from ..repos import (
    AdditionalServiceCategoryRepo as CategoryRepo,
    AdditionalServiceRepo as ServiceRepo,
    AdditionalServiceTypeRepo as ServiceTypeRepo,
    AdditionalServiceConditionStepRepo as StepRepo,
)
from ..use_cases import GetSpecCase, CategoriesAndServicesListCase, ServiceDetailCase
from ..models import ServiceSpecsResponse, CategoryDetailResponse, ServiceDetailResponse


router = APIRouter(prefix="/add-services", tags=["Доп. услуги"])


@router.get("/specs", status_code=status.HTTP_200_OK, response_model=ServiceSpecsResponse)
async def spec_view():
    resources: dict = dict(
        category_repo=CategoryRepo,
        service_type_repo=ServiceTypeRepo,
    )
    get_specs: GetSpecCase = GetSpecCase(**resources)
    return await get_specs()


@router.get(
    "", status_code=status.HTTP_200_OK, response_model=list[CategoryDetailResponse]
)
async def categories_list_view():
    """
    Список категорий и услуг
    """
    resources: dict = dict(
        category_repo=CategoryRepo,
        service_repo=ServiceRepo,
    )
    get_categories: CategoriesAndServicesListCase = CategoriesAndServicesListCase(
        **resources
    )
    return await get_categories()


@router.get(
    "/{serviceId}", status_code=status.HTTP_200_OK, response_model=ServiceDetailResponse
)
async def service_detail_view(service_id: int = Path(..., alias="serviceId")):
    """
    Деталка для услуги
    """
    resources: dict = dict(
        service_repo=ServiceRepo,
        step_repo=StepRepo,
    )
    get_service: ServiceDetailCase = ServiceDetailCase(**resources)
    return await get_service(service_id=service_id)
