from .services import ServiceResponse
from ..entities import BaseAdditionalServiceCamelCaseModel


class ServicesByTypeResponse(BaseAdditionalServiceCamelCaseModel):
    """
    Модель ответа категорий и услуг
    """

    id: int
    title: str
    results: list[ServiceResponse]

    class Config:
        orm_mode = True
