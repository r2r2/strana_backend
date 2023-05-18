from typing import Any, Type, Optional

from ...constants import UserType
from ...entities import BaseUserCase
from ...repos import UserRepo

__all__ = ('ClientsSpecsCase', 'ClientsFacetsCase',)


class ClientsSpecsCase(BaseUserCase):
    """
    Спеки пользователей
    """

    _ordering_spec_data = [
        {"label": "по убыванию фамилии", "value": "-surname"},
        {"label": "по возрастанию фамилии", "value": "surname"},
        {"label": "по убыванию старта работ", "value": "-work_start"},
        {"label": "по возрастанию старта работ", "value": "work_start"}
    ]

    def __init__(self, user_repo: Type[UserRepo]) -> None:
        self.user_repo: UserRepo = user_repo()

    async def __call__(
        self,
        agent_id: Optional[int] = None,
        agency_id: Optional[int] = None,
    ) -> dict[str, Any]:
        # фильтрация в апи
        filters: dict[str, Any] = dict(type=UserType.CLIENT)
        if agent_id:
            filters.update(dict(agent_id=agent_id))
        if agency_id:
            filters.update(dict(agency_id=agency_id))

        # агенты
        agents_filters = filters.copy()
        agents_filters.update(dict(agent__name__isnull=False))
        agents: dict[str, Any] = await self.user_repo.list(
            filters=agents_filters,
            prefetch_fields=["agent"],
        ).order_by("agent__id").distinct().values(
            "agent__id",
            "agent__name",
        )

        # проекты
        projects_filters = filters.copy()
        projects_filters.update(dict(bookings__project_id__isnull=False))
        projects: dict[str, Any] = await self.user_repo.list(
            filters=projects_filters,
            related_fields=[
                "bookings",
                "bookings__project",
            ]
        ).order_by("bookings__project__slug").distinct().values(
            "bookings__project__slug",
            "bookings__project__name",
        )

        # формируем данные для ответа
        client_specs_data = {
            "specs": {
                "agent": agents,
                "project": projects,
            },
            "ordering": self._ordering_spec_data,
        }

        return client_specs_data


class ClientsFacetsCase(BaseUserCase):
    """
    Фасеты пользователей
    """

    group: str = "agent_id"

    def __init__(self, user_repo: Type[UserRepo]) -> None:
        self.user_repo: UserRepo = user_repo()

    async def __call__(
        self,
        init_filters: dict[str, Any],
        agent_id: Optional[int] = None,
        agency_id: Optional[int] = None,
    ) -> dict[str, Any]:
        # фильтрация в апи
        filters: dict[str, Any] = dict(type=UserType.CLIENT)
        if agent_id:
            filters.update(dict(agent_id=agent_id))
        if agency_id:
            filters.update(dict(agency_id=agency_id))

        search: list[list[dict[str, Any]]] = init_filters.pop("search", [])
        init_filters.pop("ordering")
        filters.update(init_filters)
        if len(search) == 1:
            q_filters: list[Any] = [self.user_repo.q_builder(or_filters=search[0])]
        else:
            q_base: Any = self.user_repo.q_builder()
            for s in search:
                q_base |= self.user_repo.q_builder(and_filters=s)
            q_filters: list[Any] = [q_base]

        # агенты
        agents_filters = filters.copy()
        agents_filters.update(dict(agent__name__isnull=False))
        agents: list[str] = await self.user_repo.list(
            filters=agents_filters,
            q_filters=q_filters,
            prefetch_fields=["agent"],
        ).order_by("agent__id").distinct().values_list(
            "agent__id",
            flat=True,
        )

        # проекты
        projects_filters = filters.copy()
        projects_filters.update(dict(bookings__project_id__isnull=False))
        projects: list[str] = await self.user_repo.list(
            filters=projects_filters,
            q_filters=q_filters,
            related_fields=[
                "bookings",
                "bookings__project",
            ]
        ).order_by("bookings__project__slug").distinct().values_list(
            "bookings__project__slug",
            flat=True,
        )

        # формируем данные для ответа
        client_facets_data = {
            "facets": {
                "agent": agents,
                "project": projects,
            },
        }

        return client_facets_data
