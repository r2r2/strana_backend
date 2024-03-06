from ..entities import BasePrivilegeCamelCaseModel


class CategoryForFacets(BasePrivilegeCamelCaseModel):
    slug: str | None
    title: str
