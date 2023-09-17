from ..entities import BaseAdditionalServiceCamelCaseModel


class ConditionStepResponse(BaseAdditionalServiceCamelCaseModel):
    """
    Модель ответа шага для условия
    """

    id: int
    description: str
