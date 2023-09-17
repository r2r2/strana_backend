from .services import ServiceCategoryResponse
from ..entities import BaseAdditionalServiceCamelCaseModel


class CategoryDetailResponse(BaseAdditionalServiceCamelCaseModel):
    """
    Модель ответа категорий и услуг
    """

    id: int
    title: str
    services: list[ServiceCategoryResponse]

    class Config:
        orm_mode = True
