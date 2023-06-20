# pylint: disable=unused-argument
import re
from datetime import date
from typing import Any, Optional, Type

from common.dependencies import CurrentOptionalUserId, CurrentUserExtra
from common.options import InitOption as IO
from common.options import RequestOption as RO
from common.wrappers import filterize
from pydantic import Field
from pydantic import root_validator as field_overrider
from src.booking.constants import BookingStages

from ..constants import UserType
from ..entities import BaseUserFilter
from ..repos import UserRepo


async def work_period_specs(
        group: str, queryset: Any, repo: UserRepo, addition: dict[str, Any]) -> dict[str, Any]:
    """
    Спеки фильтра периода работы
    """
    specs: list[dict[str, Any]] = await repo.work_period_specs(group=group, queryset=queryset)
    if specs:
        specs: dict[str, Any] = specs[0]
    else:
        specs: list[dict[str, Any]] = []
    return specs


async def work_period_facets(
        group: str, queryset: Any, repo: UserRepo, addition: dict[str, Any]) -> dict[str, Any]:
    """
    Фасеты фильтра периода работы
    """
    facets: list[dict[str, Any]] = await repo.work_period_facets(group=group, queryset=queryset)
    if facets:
        facets: dict[str, Any] = facets[0]
    else:
        facets: list[dict[str, Any]] = []
    return facets


async def agent_specs(
        group: str, queryset: Any, repo: UserRepo, addition: dict[str, Any]
) -> list[dict[str, Any]]:
    """
    Спеки фильтра агента
    """
    specs: list[dict[str, Any]] = await repo.agent_specs(group=group, queryset=queryset)
    if not specs:
        specs = []
    return specs


async def agent_facets(
        group: str, queryset: Any, repo: UserRepo, addition: dict[str, Any]
) -> list[dict[str, Any]]:
    """
    Фасеты фильтра агента
    """
    facets: list[Any] = await repo.agents_facets(queryset=queryset, group=group)
    if not facets:
        facets = []
    return facets


@filterize
class UserFilter(BaseUserFilter):
    """
    Фильтр пользователей
    """

    search: Optional[str] = Field(alias="search", description="Поиск")
    ordering: Optional[str] = Field("id", alias="ordering", description="Сортировка")
    agent_id__in: Optional[list] = Field(alias="agent", description="Фильтр по агенту")

    # work_period: Optional[str] = Field(alias="work_period", description="Фильтр по периоду")

    # ToDo if ordering[0] == "-": TypeError: 'NoneType' object is not subscriptable
    # если что, можно захардкодить cabinet/src/users/use_cases/clients/repres.py на 20 строке
    work_start: Optional[date] = Field(alias="work_period_start", description="Фильтр по дате начала")
    work_end: Optional[date] = Field(alias="work_period_finish", description="Фильтр по дате окончания")

    # bookings__amocrm_status__name__in: Optional[list] = Field(alias="status", description="Фильтр по статусу")
    bookings__project__slug__in: Optional[list] = Field(alias="project", description="Фильтр по проекту")
    # bookings__property__type__in: Optional[list] = Field(
    #     alias="property_type", description="Фильтр по типу недвижимости")

    @field_overrider
    @classmethod
    def override_search(cls, values: dict[str, Any]) -> dict[str, Any]:
        """override"""
        search = values.get("search")
        if isinstance(search, str):
            search = search.strip()
            phone = re.sub(r'\D', '', search)
            values["search"] = [[
                dict(phone__contains=phone) if phone else {},
                dict(email__icontains=search),
                *[dict(name__icontains=word) for word in search.split()],
                *[dict(surname__icontains=word) for word in search.split()],
                *[dict(patronymic__icontains=word) for word in search.split()]
            ]]
        return values

    @field_overrider
    @classmethod
    def override_work_period(cls, values: dict[str, Any]) -> dict[str, Any]:
        """
        Override work_period field
        """

        if work_period := values.pop("work_period", None):
            components: list[str] = work_period.split("__")
            if len(components) == 2:
                try:
                    date_end: date = date.fromisoformat(components[1])
                    date_start: date = date.fromisoformat(components[0])
                    if date_start > date_end:
                        date_start, date_end = date_end, date_start
                    values["work_end__gte"]: date = date_end
                    values["work_start__lte"]: date = date_start
                except ValueError:
                    values: dict[str, Any] = values
        return values

    class Order:
        fields: dict[str, Any] = {
            "surname": "по {type} фамилии",
            "work_start": "по {type} старта работ",
        }

    class Filter:
        """
        Main class Filter for filtering user repo.
        Will be use by common/wrappers
        """
        repo: Type[UserRepo] = UserRepo

        exclude: list[str] = ["search", "ordering"]
        choices: list[str] = ["property_type"]

        additions: dict[str, Any] = {
            "work_period": [RO("agent_id", "filter_agent_id")],
            "bookings__amocrm_status__name": [
                IO("bookings__active", True),
                IO("bookings__amocrm_stage__not_in", (
                    BookingStages.DDU_FINISHED
                )),
                RO("agent_id", "filter_agent_id"),
                (
                        RO("bookings__agent_id", "filter_agent_id") |
                        RO("bookings__agency_id", "filter_agency_id")
                )
            ],
            "bookings__project__slug": [
                IO("bookings__active", True),
                RO("agent_id", "filter_agent_id"),
                (
                        RO("bookings__agent_id", "filter_agent_id") |
                        RO("bookings__agency_id", "filter_agency_id")
                )
            ],
            "bookings__property__type": [
                IO("bookings__active", True),
                RO("agent_id", "filter_agent_id"),
                (
                        RO("bookings__agent_id", "filter_agent_id") |
                        RO("bookings__agency_id", "filter_agency_id")
                )
            ],
        }
        labels: dict[str, Any] = {
            "project": "bookings__project__name",
            "status": "bookings__amocrm_status__name"
        }

        specs_overrides: dict[str, Any] = {
            "work_period": work_period_specs, "agent": agent_specs
        }
        facets_overrides: dict[str, Any] = {
            "work_period": work_period_facets, "agent": agent_facets
        }

    class Credentials:
        options: dict[str, Any] = {
            "filter_agency_id": {
                "field": "agency_id",
                "callable": CurrentUserExtra(key="agency_id")
            },
            "filter_agent_id": {
                "field": "agent_id",
                "callable": CurrentOptionalUserId(user_type=UserType.AGENT)
            },
        }
