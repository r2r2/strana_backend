from typing import Any, NamedTuple, Optional, Type, Union
from copy import copy

from common.amocrm.constants import AmoCompanyEntityType, AmoLeadQueryWith
from common.amocrm.types import AmoLead
from common.amocrm.models import Entity

from ..entities import BaseBookingCase
from ..mixins import BookingLogMixin
from ..repos import Booking, BookingRepo
from ..types import BookingAmoCRM, BookingORM


class BookingTypeNamedTuple(NamedTuple):
    price: int
    amocrm_id: Optional[int] = None


class UpdateAmoBookingService(BaseBookingCase, BookingLogMixin):
    """
    Обновление сделок в АмоСРМ после изменения в админке брокера.
    """

    def __init__(
        self,
        create_amocrm_log_task: Any,
        booking_repo: Type[BookingRepo],
        amocrm_class: Type[BookingAmoCRM],
        orm_class: Optional[Type[BookingORM]] = None,
        orm_config: Optional[dict[str, Any]] = None,
    ) -> None:
        self.amocrm_class: Type[BookingAmoCRM] = amocrm_class
        self.create_amocrm_log_task: Any = create_amocrm_log_task
        self.booking_repo: BookingRepo = booking_repo()

        self.orm_class: Union[Type[BookingORM], None] = orm_class
        self.orm_config: Union[dict[str, Any], None] = copy(orm_config)
        if self.orm_config:
            self.orm_config.pop("generate_schemas", None)

    async def __call__(
        self,
        booking_id: int,
    ) -> None:
        booking: Booking = await self.booking_repo.retrieve(
            filters=dict(id=booking_id),
            related_fields=["project", "user", "property", "agency", "agent"]
        )

        if booking and booking.amocrm_id:
            async with await self.amocrm_class() as amocrm:
                await self._update_booking_data(booking, amocrm)

    async def _update_booking_data(self, booking: Booking, amocrm: BookingAmoCRM) -> int:
        """
        Обновление данных сделки в АмоСРМ.
        """

        # достаем сделку из амо
        lead: AmoLead = await amocrm.fetch_lead(lead_id=booking.amocrm_id, query_with=[AmoLeadQueryWith.contacts])

        # находим amocrm_id всех старых агентов и агентств в сделке
        old_agents = []
        old_companies = []
        for contact in lead.embedded.contacts:
            if contact.id != booking.user.amocrm_id:
                old_agents.append(contact.id)
        if lead.embedded.companies:
            old_companies.append(lead.embedded.companies[0].id)

        # формируем для всех сущностей агентов и агентств модели
        old_entities = []
        if old_agents:
            old_agent_entities: Entity = Entity(ids=old_agents, type=AmoCompanyEntityType.contacts)
            old_entities.append(old_agent_entities)
        if old_companies:
            old_agency_entities: Entity = Entity(ids=old_companies, type=AmoCompanyEntityType.companies)
            old_entities.append(old_agency_entities)

        new_entities = []
        if booking.agent:
            agent_entities: Entity = Entity(ids=[booking.agent.amocrm_id], type=AmoCompanyEntityType.contacts)
            new_entities.append(agent_entities)
        if booking.agency:
            agency_entities: Entity = Entity(ids=[booking.agency.amocrm_id], type=AmoCompanyEntityType.companies)
            new_entities.append(agency_entities)

        # обновляем сделку в амо (основные поля)
        await amocrm.update_lead_v4(
            lead_id=booking.amocrm_id,
            city_slug=booking.project.city if booking.project else None,
            status_id=booking.amocrm_status_id,
            price=int(booking.payment_amount) if booking.payment_amount else None,
            project_amocrm_name=booking.project.amocrm_name if booking.project else None,
            project_amocrm_enum=booking.project.amocrm_enum if booking.project else None,
            project_amocrm_organization=booking.project.amocrm_organization if booking.project else None,
            project_amocrm_pipeline_id=booking.project.amo_pipeline_id if booking.project else None,
            project_amocrm_responsible_user_id=booking.project.amo_responsible_user_id if booking.project else None,
            property_id=booking.property.global_id if booking.property else None,
            property_type=booking.property.type.value.lower() if booking.property and booking.property.type else None,
        )

        # отвязываем старое агентство и старых агентов от сделки клиента в амо
        if old_entities:
            await amocrm.lead_unlink_entities(
                lead_id=lead.id,
                entities=old_entities,
            )

        # привязываем новое агентство и нового агента к сделке клиента в амо
        if new_entities:
            await amocrm.lead_link_entities(
                lead_id=lead.id,
                entities=new_entities,
            )

        # логируем изменения
        note_data: dict[str, Any] = dict(
            element="lead",
            lead_id=booking.amocrm_id,
            note="lead_changed",
            text="Изменены данные сделки в админке",
        )
        self.create_amocrm_log_task.delay(note_data=note_data)
