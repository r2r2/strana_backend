from copy import copy
from typing import Any, Optional, Type, Union

from ..repos import AgencyLogRepo
from ..entities import BaseAgencyService
from ..types import AgencyORM


class CreateAgencyLogger(BaseAgencyService):
    """
    Создание лога агентства
    """

    def __init__(
        self,
        agency_log_repo: Type[AgencyLogRepo],
        orm_class: Optional[Type[AgencyORM]] = None,
        orm_config: Optional[dict[str, Any]] = None,
    ) -> None:
        self.agency_log_repo: AgencyLogRepo = agency_log_repo()

        self.orm_class: Union[Type[AgencyORM], None] = orm_class
        self.orm_config: Union[dict[str, Any], None] = copy(orm_config)
        if self.orm_config:
            self.orm_config.pop("generate_schemas", None)

    async def __call__(self, log_data: dict[str, Any]) -> None:
        await self.agency_log_repo.create(data=log_data)
