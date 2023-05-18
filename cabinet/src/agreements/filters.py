from typing import Any, Optional, Type

from common import wrappers
from pydantic import Field
from pydantic import root_validator as field_overrider

from .entities import BaseAgreementFilter
from .repos import AgencyActRepo, AgencyAgreementRepo


@wrappers.filterize
class AgreementFilter(BaseAgreementFilter):
    """
    Фильтр договоров
    """

    search: Optional[str] = Field(alias="search", description="Поиск")

    @field_overrider
    @classmethod
    def override_search(cls, values: dict[str, Any]) -> dict[str, Any]:
        """Поиск"""
        if search := values.get("search"):
            values["search"]: list[list[dict[str, Any]]] = [
                [dict(template_name__icontains=search)]
            ]
        return values

    class Filter:
        repo: Type[AgencyAgreementRepo] = AgencyAgreementRepo


@wrappers.filterize
class ActFilter(BaseAgreementFilter):
    """
    Фильтр актов
    """

    search: Optional[str] = Field(alias="search", description="Поиск")
    booking_id__in: Optional[list] = Field(alias="bookings", description="Сделки")

    @field_overrider
    def override_search(cls, values: dict[str, Any]) -> dict[str, Any]:
        """Поиск"""
        if search := values.get("search"):
            values["search"]: list[list[dict[str, Any]]] = [
                [dict(template_name__icontains=search)]
            ]
        return values

    class Filter:
        repo: Type[AgencyActRepo] = AgencyActRepo
