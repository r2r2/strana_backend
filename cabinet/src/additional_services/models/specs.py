from ..entities import BaseAdditionalServiceCamelCaseModel


class CategoryForSpecs(BaseAdditionalServiceCamelCaseModel):
    id: int | None
    title: str


class ServiceSpecsResponse(BaseAdditionalServiceCamelCaseModel):
    """
    Модель ответа для спеков
    """

    categories: list[CategoryForSpecs]
