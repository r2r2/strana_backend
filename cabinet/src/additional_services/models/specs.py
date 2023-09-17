from ..entities import BaseAdditionalServiceCamelCaseModel


class ServiceSpecsResponse(BaseAdditionalServiceCamelCaseModel):
    """
    Модель ответа для спеков
    """

    categories: list[dict]
    service_types: list[dict]
