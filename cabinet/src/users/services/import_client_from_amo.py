import structlog

from common.amocrm import AmoCRM
from common.amocrm.constants import AmoLeadQueryWith
from common.amocrm.types import AmoContact, AmoLead
from common.amocrm.types.lead import AmoLeadContact
from src.booking.types import WebhookLead
from .create_contact import CreateContactService
from ..constants import UserType, OriginType
from ..repos import UserRepo, User, UserRoleRepo, UserRole


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
        142,  # realized
        143,  # unrealized
    ]
    ORIGIN: str = OriginType.AMOCRM
    user_type: str = UserType.CLIENT
    logger = structlog.getLogger(__name__)

    def __init__(
        self,
        user_repo: type[UserRepo],
        user_role_repo: type[UserRoleRepo],
        amocrm_class: type[AmoCRM],
    ) -> None:
        self.user_repo: UserRepo = user_repo()
        self.user_role_repo: UserRoleRepo = user_role_repo()
        self.amocrm_class: type[AmoCRM] = amocrm_class

    async def __call__(self, webhook_lead: WebhookLead) -> User | None:
        import_pipeline_id, import_status_id = (
            webhook_lead.pipeline_id,
            webhook_lead.new_status_id,
        )
        if (
            import_pipeline_id not in self.import_pipelines_ids
            or import_status_id not in self.import_statuses_ids
        ):
            return

        lead_id: int = webhook_lead.lead_id
        async with await self.amocrm_class() as amocrm:
            amo_lead: AmoLead | None = await amocrm.fetch_lead(
                lead_id=lead_id, query_with=[AmoLeadQueryWith.contacts]
            )
            if not amo_lead:
                self.logger.warning("Lead has not found at amo")
                return

            user_amocrm_id: int | None = self._get_contact_id(amo_lead=amo_lead)
            contact: AmoContact | None = await amocrm.fetch_contact(
                user_id=user_amocrm_id
            )
            if not contact:
                self.logger.warning("User has not found at amo contact")
                return

            data: dict = await self.fetch_amocrm_data(contact)
            user_role: UserRole = await self.user_role_repo.retrieve(
                filters=dict(slug=self.user_type)
            )
            phone: str = data.get("phone")
            user_by_phone: User | None = await self.user_repo.retrieve(
                filters=dict(phone=phone, role=user_role)
            )
            user_by_amocrm_id: User | None = await self.user_repo.retrieve(
                filters=dict(amocrm_id=user_amocrm_id, role=user_role)
            )
            found_user = user_by_phone or user_by_amocrm_id
            if found_user:
                updated_user: User = await self.user_repo.update(
                    model=found_user, data=data
                )
            else:
                data.update(
                    amocrm_id=user_amocrm_id,
                    type=self.user_type,
                    origin=self.ORIGIN,
                    role=user_role,
                )
                updated_user: User = await self.user_repo.create(data=data)

            return updated_user

    def _get_contact_id(self, amo_lead: AmoLead) -> int | None:
        if contacts := amo_lead.embedded.contacts:
            contact: AmoLeadContact = contacts[0]
            if contact.is_main:
                return contact.id
        self.logger.warning("User has not found at amo contact")
