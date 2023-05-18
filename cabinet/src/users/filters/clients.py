import re
from datetime import date
from typing import Any, Optional, Type

from common.wrappers import filterize
from pydantic import Field
from pydantic import root_validator as field_overrider
from src.users.entities import BaseUserFilter
from src.users.repos import UserRepo


@filterize
class ClientsFilter(BaseUserFilter):
    """Фильтр страницы клиентов у АН"""
    search: Optional[str] = Field(alias="search", description="Поиск")
    ordering: Optional[str] = Field(alias="ordering", description="Сортировка")
    user_checks__status: Optional[str] = Field(alias="status", description="Статус")
    bookings__property__type__in: Optional[list] = Field(alias="property_type", description="Тип недвижимости")
    bookings__project__slug__in: Optional[list] = Field(alias="project", description="Проект")
    agent_id__in: Optional[list[int]] = Field(alias="agents", description="Агенты")
    agency_id__in: Optional[list[int]] = Field(alias="agencies", description="Агенства")
    work_end: Optional[date] = Field(alias="work_period_finish", description="Фильтр по дате начала")
    work_start: Optional[date] = Field(alias="work_period_start", description="Фильтр по дате окончания")
    is_active: Optional[bool] = Field(alias="is_active", description="Активность клиента")
    agent_id__isnull: bool = False
    amocrm_id__isnull: bool = False

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

    class Filter:
        repo: Type[UserRepo] = UserRepo

        exclude: list[str] = ["search"]
