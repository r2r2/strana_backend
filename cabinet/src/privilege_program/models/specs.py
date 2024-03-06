from ..entities import BasePrivilegeCamelCaseModel


class CategoryForSpecs(BasePrivilegeCamelCaseModel):
    slug: str | None
    title: str | None


class PrivilegeSpecsResponse(BasePrivilegeCamelCaseModel):
    """
    Модель ответа для спеков
    """

    categories: list[CategoryForSpecs]
