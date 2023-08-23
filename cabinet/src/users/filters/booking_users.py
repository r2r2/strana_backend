import re
from datetime import date
from typing import Any, Optional, Type

from common.options import InitOption as IO
from common.options import RequestOption as RO
from common.wrappers import filterize
from pydantic import Field
from pydantic import root_validator as field_overrider
from src.booking.constants import BookingStages
from src.booking.repos import BookingRepo
from src.users.entities import BaseUserFilter


@filterize
class BookingUserFilter(BaseUserFilter):
    search: Optional[str] = Field(alias="search", description="Поиск")
    ordering: Optional[str] = Field(alias="ordering", description="Сортировка")
    agent_id__in: Optional[list] = Field(alias="agent", description="Фильтр по агенту")
    active: Optional[str] = Field(alias="active", description="Активность")
    amocrm_status__group_status__name__in: Optional[list] = Field(
        alias="status", description="Фильтр по групповому статусу")
    project__slug__in: Optional[list] = Field(
        alias="project", description="Фильтр по проекту")
    property__property_type__slug__in: Optional[list] = Field(
        alias="propertyType", description="Фильтр по типу недвижимости")
    # либо work_period_start попадает  [user__work_start, user__work_end], либо work_period_end
    user_id__in: Optional[list] = Field(alias="clients", description="Фильтр по клиентам")
    user__work_end__lte: Optional[date] = Field(alias="work_period_finish", description="Фильтр по дате начала")
    user__work_start__gte: Optional[date] = Field(alias="work_period_start", description="Фильтр по дате окончания")

    @field_overrider
    @classmethod
    def override_search(cls, values: dict[str, Any]) -> dict[str, Any]:
        """search"""
        search = values.get("search")
        if isinstance(search, str):
            search = search.strip()
            phone = re.sub(r'\D', '', search)
            values["search"] = [[
                dict(user__email__icontains=search),
                dict(user__phone__contains=phone) if phone else {},
                *[dict(user__name__icontains=word) for word in search.split()],
                *[dict(user__surname__icontains=word) for word in search.split()],
                *[dict(user__patronymic__icontains=word) for word in search.split()]
            ]]
        return values

    class Order:
        fields: dict[str, Any] = {
            "user__surname": "по {type} имени",
            "project__name": "по {type} названию ЖК"
        }

    class Filter:
        """
        Will be used by common/specs_wrappers
        """
        repo: Type[BookingRepo] = BookingRepo

        exclude: list[str] = ["search", "ordering"]
        choices: list[str] = ["property"]

        additions: dict[str, Any] = {
            "amocrm_status__name": [
                IO("amocrm_stage__not_in", (
                    BookingStages.DDU_FINISHED
                )),
                RO("agent_id", "filter_agent_id"),
                (
                        RO("agent_id", "filter_agent_id") |
                        RO("agency_id", "filter_agency_id")
                )
            ],
            "user__work_end": [
                RO("agent_id", "filter_agent_id"),
                (
                        RO("agent_id", "filter_agent_id") |
                        RO("agency_id", "filter_agency_id")
                ),
            ],
            "user__work_start": [
                IO("user__work_start__isnull", False),
                RO("agent_id", "filter_agent_id"),
                (
                        RO("agent_id", "filter_agent_id") |
                        RO("agency_id", "filter_agency_id")
                )
            ],
            "project__slug": [
                RO("agent_id", "filter_agent_id"),
                (
                        RO("agent_id", "filter_agent_id") |
                        RO("agency_id", "filter_agency_id")
                )
            ],
            "property__type": [
                RO("agent_id", "filter_agent_id"),
                (
                        RO("agent_id", "filter_agent_id") |
                        RO("agency_id", "filter_agency_id")
                )
            ],
        }
        labels: dict[str, Any] = {
            "project": "project__name",
            "status": "amocrm_status__name",
            "agent": "agent__name",
            "property": "property__type",
            "work_start": "user__work_end",
            "work_finish": "user__work_start",
            "active": "active",
            "clients": "user__name",
            "work_period_finish": "user__work_end",
            "work_period_start": "user__work_start",
        }

    # class Credentials:
    #     options: dict[str, Any] = {
    #         "filter_agency_id": {
    #             "field": "agency_id",
    #             "callable": CurrentUserExtra(key="agency_id")
    #         },
    #         "filter_agent_id": {
    #             "field": "agent_id",
    #             "callable": CurrentOptionalUserId(user_type=UserType.AGENT)
    #         },
    #     }
