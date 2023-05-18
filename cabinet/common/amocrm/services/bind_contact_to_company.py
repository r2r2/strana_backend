from copy import copy
from typing import Type, Optional

import tortoise

from common.amocrm import AmoCRM
from common.amocrm.constants import AmoCompanyEntityType
from common.amocrm.entities import BaseAmocrmService


class BindContactCompanyService(BaseAmocrmService):
    """Сервис для привязки контакта к компании"""

    def __init__(
            self,
            amocrm_class: Type[AmoCRM],
            orm_class: Optional[Type[tortoise.Tortoise]],
            orm_config: Optional[dict],
    ):
        self.amocrm_class = amocrm_class
        self.orm_class = orm_class
        self.orm_config = copy(orm_config)
        if self.orm_config:
            self.orm_config.pop("generate_schemas", None)

    async def __call__(self, agency_amocrm_id: int, agent_amocrm_id: int):
        async with await self.amocrm_class() as amocrm:
            await amocrm.bind_entity(
                agency_amocrm_id=agency_amocrm_id,
                entity_id=agent_amocrm_id,
                entity_type=AmoCompanyEntityType.contacts
            )
