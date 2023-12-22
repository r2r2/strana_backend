from datetime import datetime, timedelta
from typing import Any

from common.amocrm import AmoCRM
from common.amocrm.constants import AmoContactQueryWith, AmoLeadQueryWith
from common.amocrm.types import AmoContact, AmoLead
from common.utils import partition_list
from config import EnvTypes, maintenance_settings
from src.agents.services.import_clients import LeadStatuses
from src.cities.exceptions import CityNotFoundError
from src.cities.repos import CityRepo, City
from src.dashboard.entities import BaseDashboardCase
from src.dashboard.repos import TicketRepo, Ticket
from src.users.models import RequestCreateTicket


class CreateTicketCase(BaseDashboardCase):
    """
    Сценарий создания заявки
    """
    note_template: str = """
        {title} 
        Заголовок карточки: {card_title}
        Имя: {name}
        Контактный номер телефона: {phone}
    """
    tags: list[str] = ["ЛК клиента", "Обратный звонок"]
    dev_test_booking_tag: list[str] = ['Тестовая бронь']
    stage_test_booking_tag: list[str] = ['Тестовая бронь Stage']

    def __init__(
        self,
        ticket_repo: type[TicketRepo],
        city_repo: type[CityRepo],
        amocrm_class: type[AmoCRM],
        amocrm_config: dict[str, Any],
    ):
        self.ticket_repo: TicketRepo = ticket_repo()
        self.city_repo: CityRepo = city_repo()
        self.amocrm_class: type[AmoCRM] = amocrm_class
        self.partition_limit: int = amocrm_config["partition_limit"]

        self.create_manager_task: bool = False

        # note: временный ответственный, пока не известна логика получения
        self.responsible_manager_amocrm_id = 6541746

    async def __call__(self, payload: RequestCreateTicket) -> None:
        city: City = await self.city_repo.retrieve(
            filters=dict(slug=payload.city),
        )
        if not city:
            raise CityNotFoundError

        data: dict[str, Any] = dict(
            name=payload.name,
            phone=payload.phone,
            type=payload.type,
        )
        ticket: Ticket = await self.ticket_repo.create(data=data)
        await ticket.city.add(city)

        amo_note: str = await self.get_amo_note(payload=payload, ticket=ticket)
        await self.process_amocrm(
            payload=payload,
            city=city,
            amo_note=amo_note,
            ticket=ticket,
        )

    async def process_amocrm(
        self,
        payload: RequestCreateTicket,
        city: City,
        amo_note: str,
        ticket: Ticket,
    ) -> None:
        """
        Обработка АМО
        """
        async with await self.amocrm_class() as amocrm:
            await self.amocrm_handler(
                amocrm=amocrm,
                payload=payload,
                city=city,
                amo_note=amo_note,
                ticket=ticket,
            )

    async def get_amo_note(self, payload: RequestCreateTicket, ticket: Ticket) -> str:
        """
        Получение текста примечания для АМО
        """
        if payload.type == "callback":
            title: str = "Заявка на обратный звонок"
        else:
            title: str = "Заявка на паркинг и кладовые"

        amo_note_data: dict = dict(
            name=ticket.name,
            phone=ticket.phone,
            title=title,
            card_title=payload.card_title,
        )

        return self.note_template.format(**amo_note_data)

    async def _fetch_contact_leads(self, amocrm: AmoCRM, contact: AmoContact) -> list[AmoLead]:
        """
        Найти сделки контакта в амо
        @param contact: AmoContact
        @return: list[AmoLead]
        """
        big_lead_ids: list[int] = [lead.id for lead in contact.embedded.leads]
        if not big_lead_ids:
            return []
        leads = []
        for lead_ids in partition_list(big_lead_ids, self.partition_limit):
            leads.extend(await amocrm.fetch_leads(lead_ids=lead_ids, query_with=[AmoLeadQueryWith.contacts]))
        return leads

    async def amocrm_handler(
        self,
        amocrm: AmoCRM,
        payload: RequestCreateTicket,
        city: City,
        amo_note: str,
        ticket: Ticket,
    ) -> None:
        contacts: list[AmoContact] = await amocrm.fetch_contacts(
            user_phone=payload.phone,
            query_with=[AmoContactQueryWith.leads],
        )

        if contacts:
            amocrm_contact_id: int = contacts[0].id

        else:
            contacts: list[Any] = await amocrm.create_contact(
                user_name=payload.name, user_phone=payload.phone
            )
            amocrm_contact_id: int = contacts[0]["id"]

        contact: AmoContact = await amocrm.fetch_contact(
            user_id=amocrm_contact_id, query_with=[AmoContactQueryWith.leads]
        )
        contact_leads: list[AmoLead] = await self._fetch_contact_leads(amocrm, contact=contact)

        active_leads: list[AmoLead] = [
            lead for lead in contact_leads if
            lead.status_id not in (LeadStatuses.REALIZED, LeadStatuses.UNREALIZED)
        ]
        if active_leads:
            amocrm_lead_id: int = active_leads[0].id
            complete_till_datetime: datetime = datetime.now() + timedelta(days=2)
            await amocrm.create_task_v4(
                element_id=amocrm_lead_id,
                text=amo_note,
                complete_till=int(complete_till_datetime.timestamp()),
                responsible_user_id=amocrm_contact_id,
            )
        else:
            tags = self.tags
            if maintenance_settings["environment"] == EnvTypes.DEV:
                tags = tags + self.dev_test_booking_tag
            elif maintenance_settings["environment"] == EnvTypes.STAGE:
                tags = tags + self.stage_test_booking_tag

            leads: list[AmoLead] = await amocrm.create_lead(
                city_slug=city.slug,
                user_amocrm_id=amocrm_contact_id,
                status_id=self.amocrm_class.start_status_id,
                tags=tags,
                project_amocrm_responsible_user_id=self.responsible_manager_amocrm_id,
                project_amocrm_pipeline_id=self.amocrm_class.start_pipeline_id,
            )
            amocrm_lead_id: int = leads[0].id

        await amocrm.create_note(lead_id=amocrm_lead_id, note="common", text=amo_note, element="lead")

        amo_data: dict = dict(
            user_amocrm_id=amocrm_contact_id,
            booking_amocrm_id=amocrm_lead_id,
            note=amo_note,
        )
        await self.ticket_repo.update(model=ticket, data=amo_data)
