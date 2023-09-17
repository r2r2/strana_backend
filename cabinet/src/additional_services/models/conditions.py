from .steps import ConditionStepResponse
from ..entities import BaseAdditionalServiceCamelCaseModel


class ServiceConditionResponse(BaseAdditionalServiceCamelCaseModel):
    """
    Модель ответа условия для услуги
    """

    id: int
    title: str
    steps: list[ConditionStepResponse]

    class Config:
        orm_mode = True
