from copy import copy
from typing import Type, Optional, Any, Union

from ..entities import BaseShowTimeService
from ..repos import ShowTimeRepo, ShowTime
from ..types import ShowTimeORM, ShowTimeAmoCRM


class CreateShowTimeService(BaseShowTimeService):

    def __init__(
        self,
        showtime_repo: Type[ShowTimeRepo],
        amocrm_class: Type[ShowTimeAmoCRM],
        orm_class: Optional[Type[ShowTimeORM]] = None,
        orm_config: Optional[dict[str, Any]] = None,
    ) -> None:
        self.showtime_repo: ShowTimeRepo = showtime_repo()

        self.amocrm_class: Type[ShowTimeAmoCRM] = amocrm_class

        self.orm_class: Union[Type[ShowTimeORM], None] = orm_class
        self.orm_config: Union[dict[str, Any], None] = copy(orm_config)
        if self.orm_config:
            self.orm_config.pop("generate_schemas", None)

    async def __call__(
        self,
        showtime_id: Optional[int] = None,
    ) -> int:
        filters: dict[str, Any] = dict(id=showtime_id)
        showtime: ShowTime = await self.showtime_repo.retrieve(
            filters=filters, related_fields=["user", "agent", "project", "project__city"]
        )
        async with await self.amocrm_class() as amocrm:
            data: dict[str, Any] = dict(
                visit=showtime.visit,
                city_slug=showtime.project.city.slug,
                property_type=showtime.property_type,
                user_amocrm_id=showtime.user.amocrm_id,
                agent_amocrm_id=showtime.agent.amocrm_id,
                project_amocrm_name=showtime.project.amocrm_name,
                project_amocrm_enum=showtime.project.amocrm_enum
            )
            data: list[Any] = await amocrm.create_showtime(**data)
            amocrm_id: int = data[0]["id"]
            data: dict[str, Any] = dict(amocrm_id=amocrm_id)
            await self.showtime_repo.update(showtime, data=data)
            await amocrm.update_showtime(lead_id=amocrm_id)
        return amocrm_id

