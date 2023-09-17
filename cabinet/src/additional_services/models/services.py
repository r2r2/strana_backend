from collections import OrderedDict

from .conditions import ServiceConditionResponse
from ..entities import BaseAdditionalServiceCamelCaseModel


class ServiceCategoryResponse(BaseAdditionalServiceCamelCaseModel):
    """
    Модель ответа услуги для категории
    """

    id: int
    title: str
    announcement: str
    description: str
    hint: str
    image_preview: OrderedDict
    image_detailed: OrderedDict
    kind_id: int


class ServiceDetailResponse(BaseAdditionalServiceCamelCaseModel):
    """
    Модель ответа деталки услуги
    """

    id: int
    title: str
    announcement: str
    description: str
    hint: str
    image_preview: OrderedDict
    image_detailed: OrderedDict
    condition: ServiceConditionResponse

    class Config:
        orm_mode = True
