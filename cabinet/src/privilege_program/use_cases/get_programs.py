from datetime import datetime

from tortoise.queryset import QuerySet

from ..entities import BasePrivilegeServiceCase
from ..repos import (
    PrivilegeProgramRepo,
    PrivilegeCategoryRepo,
    PrivilegeCategory,
)


class ProgramListCase(BasePrivilegeServiceCase):
    """
    Кейс получения списка программ по категориям
    """

    def __init__(
        self,
        program_repo: type[PrivilegeProgramRepo],
        category_repo: type[PrivilegeCategoryRepo],
    ) -> None:
        self.program_repo: PrivilegeProgramRepo = program_repo()
        self.category_repo: PrivilegeCategoryRepo = category_repo()

    async def __call__(self, category_slugs: list[str], city: str | None) -> list[PrivilegeCategory]:
        program_filters: dict = dict(is_active=True)
        program_to_deactivate = await self.program_repo.list(filters=program_filters)

        for program in program_to_deactivate:
            if program.until is not None and program.until.timestamp() < datetime.now().timestamp():
                await self.category_repo.update(model=program, data=dict(is_active=False))

        category_filters: dict = dict(is_active=True)
        if city is not None:
            filtered_categories_slug = []
            for category in await self.category_repo.list(filters=category_filters):
                if city in [city.slug for city in await category.cities] or city is None:
                    filtered_categories_slug.append(category.slug)
            category_filters.update(slug__in=filtered_categories_slug)

        if category_slugs:
            category_filters.update(slug__in=category_slugs)
            program_filters.update(category_id__in=category_slugs)

        program_qs: QuerySet = self.program_repo.list(
            filters=program_filters,
            prefetch_fields=["partner_company", "subcategory"],
            ordering="priority_in_subcategory",
        )
        categories: list[PrivilegeCategory] = await self.category_repo.list(
            filters=category_filters,
            prefetch_fields=[
                dict(
                    relation="programs",
                    queryset=program_qs,
                    to_attr="results",
                )
            ],
            ordering="dashboard_priority",
        )
        return categories
