from typing import Any, Type, Optional

from src.booking.repos import BookingRepo

from ...constants import UserType
from ...entities import BaseUserCase

__all__ = ('BookingsSpecsCase', 'BookingsFacetsCase',)


class BookingsSpecsCase(BaseUserCase):
    """
    Спеки сделок
    """

    _ordering_spec_data = [
        {"label": "по убыванию имени", "value": "-user__surname"},
        {"label": "по возрастанию имени", "value": "user__surname"},
        {"label": "по убыванию названию ЖК", "value": "-project__name"},
        {"label": "по возрастанию названию ЖК", "value": "project__name"}
    ]

    def __init__(self, booking_repo: Type[BookingRepo]) -> None:
        self.booking_repo: BookingRepo = booking_repo()

    async def __call__(
        self,
        agent_id: Optional[int] = None,
        agency_id: Optional[int] = None,
    ) -> dict[str, Any]:
        # фильтрация в апи
        filters: dict[str, Any] = dict(user__type=UserType.CLIENT)
        if agent_id:
            filters.update(dict(agent_id=agent_id))
        if agency_id:
            filters.update(dict(agency_id=agency_id))

        # агенты
        agents_filters = filters.copy()
        agents_filters.update(dict(agent__name__isnull=False))
        agents: dict[str, Any] = await self.booking_repo.list(
            filters=agents_filters,
            related_fields=["agent"],
        ).distinct().values(
            "agent__id",
            "agent__name",
        )

        # статусы сделок
        statuses_filters = filters.copy()
        statuses_filters.update(dict(amocrm_status__group_status_id__isnull=False))
        statuses: list[Any] = await self.booking_repo.list(
            filters=statuses_filters,
            related_fields=[
                "amocrm_status",
                "amocrm_status__group_status",
            ],
        ).order_by(
            "amocrm_status__group_status__sort",
        ).distinct().values(
            "amocrm_status__group_status__sort",
            "amocrm_status__group_status__name",
        )

        # проекты
        projects_filters = filters.copy()
        projects_filters.update(dict(project_id__isnull=False))
        projects: dict[str, Any] = await self.booking_repo.list(
            filters=projects_filters,
            related_fields=["project"],
        ).distinct().values(
            "project__slug",
            "project__name"
        )

        # объекты нежвижимости
        properties_filters = filters.copy()
        properties_filters.update(dict(property__type__isnull=False))
        properties: list[Any] = await self.booking_repo.list(
            filters=properties_filters,
            related_fields=["property"],
        ).distinct().values_list(
            "property__type",
            flat=True,
        )

        # формируем данные для ответа
        booking_specs_data = {
            "specs": {
                "agent": agents,
                "status": [
                    dict(
                        value=status.get("amocrm_status__group_status__name"),
                        label=status.get("amocrm_status__group_status__name"),
                    ) for status in statuses
                ],
                "project": projects,
                "property": properties,
            },
            "ordering": self._ordering_spec_data,
        }

        return booking_specs_data


class BookingsFacetsCase(BaseUserCase):
    """
    Фасеты сделок
    """

    def __init__(self, booking_repo: Type[BookingRepo]) -> None:
        self.booking_repo: BookingRepo = booking_repo()

    async def __call__(
        self,
        init_filters: dict[str, Any],
        agent_id: Optional[int] = None,
        agency_id: Optional[int] = None,
    ) -> dict[str, Any]:
        # фильтрация в апи
        filters: dict[str, Any] = dict(user__type=UserType.CLIENT)
        if agent_id:
            filters.update(dict(agent_id=agent_id))
        if agency_id:
            filters.update(dict(agency_id=agency_id))

        search: list[list[dict[str, Any]]] = init_filters.pop("search", [])
        filters.update(init_filters)
        if len(search) == 1:
            q_filters: list[Any] = [self.booking_repo.q_builder(or_filters=search[0])]
        else:
            q_base: Any = self.booking_repo.q_builder()
            for s in search:
                q_base |= self.booking_repo.q_builder(and_filters=s)
            q_filters: list[Any] = [q_base]

        # агенты
        agents_filters = filters.copy()
        agents_filters.update(dict(agent__name__isnull=False))
        agents: list[int] = await self.booking_repo.list(
            filters=agents_filters,
            q_filters=q_filters,
            related_fields=["agent"],
        ).distinct().values_list(
            "agent__id",
            flat=True,
        )

        # статусы сделок
        statuses_filters = filters.copy()
        statuses_filters.update(dict(amocrm_status__group_status_id__isnull=False))
        statuses: list[Any] = await self.booking_repo.list(
            filters=statuses_filters,
            q_filters=q_filters,
            related_fields=[
                "amocrm_status",
                "amocrm_status__group_status",
            ],
        ).order_by(
            "amocrm_status__group_status__sort",
        ).distinct().values(
            "amocrm_status__group_status__sort",
            "amocrm_status__group_status__name",
        )

        # проекты
        projects_filters = filters.copy()
        projects_filters.update(dict(project_id__isnull=False))
        projects: list[str] = await self.booking_repo.list(
            filters=projects_filters,
            q_filters=q_filters,
            related_fields=["project"],
        ).distinct().values_list(
            "project__slug",
            flat=True,
        )

        # объекты нежвижимости
        properties_filters = filters.copy()
        properties_filters.update(dict(property__type__isnull=False))
        properties: list[Any] = await self.booking_repo.list(
            filters=properties_filters,
            q_filters=q_filters,
            related_fields=["property"],
        ).distinct().values_list(
            "property__type",
            flat=True,
        )

        booking_facets_data = {
            "facets": {
                "agent": agents,
                "status": [status.get("amocrm_status__group_status__name") for status in statuses],
                "project": projects,
                "property": [property.value for property in properties],
            },
        }

        return booking_facets_data
