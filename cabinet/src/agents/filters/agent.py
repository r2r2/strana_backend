from re import match
from typing import Any, Optional, Type

from common.wrappers import filterize
from pydantic import Field
from pydantic import root_validator as field_overrider

from ..entities import BaseAgentFilter
from ..repos import AgentRepo


@filterize
class AgentFilter(BaseAgentFilter):
    """
    Фильтр агентов
    """

    search: Optional[str] = Field(alias="search", description="Поиск")
    ordering: Optional[str] = Field(alias="ordering", description="Сортировка")
    agency_id__in: Optional[list] = Field(alias="agency", description="Фильтр по агенству")

    @field_overrider
    def override_search(cls, values: dict[str, Any]) -> dict[str, Any]:
        """override search"""
        phone_regex: str = r"^[0-9\s]{1,20}$"
        if search := values.get("search"):
            contained_plus: bool = "+" in search
            search: str = search.replace("+", "").replace("-", "").replace("(", "").replace(")", "")
            if match(phone_regex, search) or contained_plus:
                search: str = search.replace(" ", "").replace("_", "")
                values["search"]: list[list[dict[str, Any]]] = [
                    [dict(phone__icontains=search)]
                ]
            elif search.isascii():
                values["search"]: list[list[dict[str, Any]]] = [
                    [dict(email__icontains=search)]
                ]
            else:
                components: list[str] = search.split(" ")
                if len(components) == 1:
                    values["search"]: list[list[dict[str, Any]]] = [
                        [
                            dict(name__icontains=search),
                            dict(surname__icontains=search),
                            dict(patronymic__icontains=search)
                        ]
                    ]
                elif len(components) == 2:
                    values["search"]: list[dict[str, Any]] = [
                        [
                            dict(name__icontains=components[0]),
                            dict(surname__icontains=components[1])
                        ],
                        [
                            dict(surname__icontains=components[0]),
                            dict(name__icontains=components[1]),

                        ],
                        [
                            dict(name__icontains=components[0]),
                            dict(patronymic__icontains=components[1])
                        ],
                        [
                            dict(patronymic__icontains=components[0]),
                            dict(name__icontains=components[1]),

                        ],

                        [
                            dict(surname__icontains=components[0]),
                            dict(patronymic__icontains=components[1]),

                        ],
                        [
                            dict(patronymic__icontains=components[0]),
                            dict(surname__icontains=components[1]),
                        ],
                    ]
                elif len(components) == 3:
                    values["search"]: list[list[dict[str, Any]]] = [
                        [
                            dict(name__icontains=components[0]),
                            dict(surname__icontains=components[1]),
                            dict(patronymic__icontains=components[2])

                        ],
                        [
                            dict(name__icontains=components[0]),
                            dict(surname__icontains=components[2]),
                            dict(patronymic__icontains=components[1])

                        ],
                        [
                            dict(name__icontains=components[1]),
                            dict(surname__icontains=components[0]),
                            dict(patronymic__icontains=components[2])

                        ],
                        [
                            dict(name__icontains=components[1]),
                            dict(surname__icontains=components[2]),
                            dict(patronymic__icontains=components[0])

                        ],
                        [
                            dict(name__icontains=components[2]),
                            dict(surname__icontains=components[0]),
                            dict(patronymic__icontains=components[1])

                        ],
                        [
                            dict(name__icontains=components[2]),
                            dict(surname__icontains=components[1]),
                            dict(patronymic__icontains=components[0])

                        ]
                    ]
                else:
                    values["search"]: list[dict[str, Any]] = []
        return values

    class Order:
        fields: dict[str, Any] = {
            "name": "по {type} имени",
        }

    class Filter:
        repo: Type[AgentRepo] = AgentRepo
        exclude: list[str] = ["search", "ordering"]
        labels: dict[str, Any] = {
            "agency": "agency__name",
            "booking": "booking__amocrm_status_id"
        }
