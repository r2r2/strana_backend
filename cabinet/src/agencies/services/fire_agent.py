from copy import copy
from typing import Any, Optional, Type, Union

from common.amocrm import AmoCRM
from common.amocrm.constants import AmoCompanyEntityType, AmoContactQueryWith
from common.amocrm.types import AmoContact
from common.amocrm.models import Entity

from ..entities import BaseAgencyService
from ..types import AgencyORM


class FireAgentService(BaseAgencyService):
    """
    Увольнение агента в AmoCRM.
    """

    def __init__(
        self,
        amocrm_class: Type[AmoCRM],
        orm_class: Optional[Type[AgencyORM]] = None,
        orm_config: Optional[dict[str, Any]] = None,
    ) -> None:
        self.amocrm_class: Type[AmoCRM] = amocrm_class

        self.orm_class: Union[Type[AgencyORM], None] = orm_class
        self.orm_config: Union[dict[str, Any], None] = copy(orm_config)
        if self.orm_config:
            self.orm_config.pop("generate_schemas", None)

    async def __call__(
        self,
        agent_amocrm_id: int,
        repres_amocrm_id: int,
        agency_amocrm_id: int,
    ) -> None:
        async with await self.amocrm_class() as amocrm:
            # получаем все сделки агента из амо
            contact: Optional[AmoContact] = await amocrm.fetch_contact(
                user_id=agent_amocrm_id, query_with=[AmoContactQueryWith.leads]
            )
            lead_ids: list[int] = [lead.id for lead in contact.embedded.leads]

            # формируем для агента и представителя модели сущностей для передачи в амо
            agent_entity: Entity = Entity(ids=[agent_amocrm_id], type=AmoCompanyEntityType.contacts)
            repres_entity: Entity = Entity(ids=[repres_amocrm_id], type=AmoCompanyEntityType.contacts)

            # отвязываем агента от всех сделок в амо
            await amocrm.leads_unlink_entities(
                lead_ids=lead_ids,
                entities=[agent_entity],
            )

            # привязываем представителя ко всем сделкам уволенного агента в амо
            await amocrm.leads_link_entities(
                lead_ids=lead_ids,
                entities=[repres_entity],
            )

            # отвязываем агента от агентства в амо
            await amocrm.unbind_entity(
                agency_amocrm_id=agency_amocrm_id,
                entity_id=agent_amocrm_id,
                entity_type=AmoCompanyEntityType.contacts,
            )
