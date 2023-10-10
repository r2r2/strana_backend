from ..entities import BaseAdditionalServiceCamelCaseModel


class CategoryForFacets(BaseAdditionalServiceCamelCaseModel):
    id: int | None
    title: str


class ServiceFacetsResponse(BaseAdditionalServiceCamelCaseModel):
    """
    Модель ответа для спеков
    """

    categories: list[CategoryForFacets]
