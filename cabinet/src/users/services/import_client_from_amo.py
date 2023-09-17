import structlog
from typing import Optional, Type

from common.amocrm import AmoCRM
from common.amocrm.constants import AmoLeadQueryWith
from common.amocrm.types import AmoContact, AmoLead
from common.amocrm.types.lead import AmoLeadContact
from src.booking.types import WebhookLead
from .create_contact import CreateContactService
from ..constants import UserType, OriginType
from ..repos import UserRepo, User


class ImportContactFromAmoService(CreateContactService):
    """
    Импорт данных контакта из АМО
    """
    import_pipelines_ids: list[int] = [3934218, 1941865, 3568449, 5798376, 1305043]
    import_statuses_ids: list[int] = [
        37592463,
        40127295,
        37592541,
        40127292,
        45598248,
        45598251,
        29096401,
        36204951,
        41182452,
        35065584,
        21189706,
        21189709,
        21197641,
        50814930,
        50814843,
        50814939,
        57272765,
    ]
    ORIGIN: str = OriginType.AMOCRM
    logger = structlog.getLogger(__name__)
    def __init__(
            self,
            user_repo: Type[UserRepo],
            amocrm_class: Type[AmoCRM],
    ) -> None:
        self.user_repo: UserRepo = user_repo()
        self.amocrm_class: Type[AmoCRM] = amocrm_class

    async def __call__(self, webhook_lead: WebhookLead) -> User:
        import_pipeline_id, import_status_id = webhook_lead.pipeline_id, webhook_lead.new_status_id
        if import_pipeline_id in self.import_pipelines_ids and import_status_id in self.import_statuses_ids:
            lead_id: int = webhook_lead.lead_id
            async with await self.amocrm_class() as amocrm:
                amo_lead: Optional[AmoLead] = await amocrm.fetch_lead(
                    lead_id=lead_id, query_with=[AmoLeadQueryWith.contacts]
                )
                if not amo_lead:
                    self.logger.warning("Lead has not found at amo")
                    return
                user_amocrm_id: Optional[int] = self._get_contact_id(amo_lead=amo_lead)
                contact: Optional[AmoContact] = await amocrm.fetch_contact(user_id=user_amocrm_id)
                if not contact:
                    self.logger.warning("User has not found at amo contact")
                    return
                data: dict = self.fetch_amocrm_data(contact)
                data.update(amocrm_id=user_amocrm_id, type=UserType.CLIENT, origin=self.ORIGIN)
                phone: str = data.pop("phone")
                return await self.user_repo.update_or_create(filters=dict(phone=phone), data=data)

    def _get_contact_id(self, amo_lead: AmoLead) -> Optional[int]:
        if contacts := amo_lead.embedded.contacts:
            contact: AmoLeadContact = contacts[0]
            if contact.is_main:
                return contact.id
        self.logger.warning("User has not found at amo contact")
        return
