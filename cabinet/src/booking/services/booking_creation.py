import structlog
from datetime import datetime
from typing import Optional, Callable

from common.amocrm import AmoCRM
from config import site_config
from common.unleash.client import UnleashClient
from config.feature_flags import FeatureFlags
from src.amocrm.repos import AmocrmStatus
from src.projects.repos import Project, ProjectRepo
from src.properties.constants import PremiseType, PropertyTypes
from src.properties.repos import Property, PropertyRepo
from src.properties.services import ImportPropertyService
from src.payments.repos import PurchaseAmoMatrix, PurchaseAmoMatrixRepo

from ..constants import BookingCreatedSources, BookingStages
from ..entities import BaseBookingService
from src.booking.repos import BookingRepo, Booking, BookingSource
from ..types import WebhookLead, CustomFieldValue
from src.booking.utils import get_booking_source
from src.projects.constants import ProjectStatus


class BookingCreationFromAmoService(BaseBookingService):
    """
    Создание сделки из АМО
    """
    CREATED_SOURCE: str = BookingCreatedSources.AMOCRM
    BOOKING_STAGE: str = BookingStages.BOOKING
    SITE_HOST: str = site_config["site_host"]
    logger = structlog.getLogger(__name__)

    def __init__(
        self,
        amocrm_class: type[AmoCRM],
        project_repo: type[ProjectRepo],
        property_repo: type[PropertyRepo],
        booking_repo: type[BookingRepo],
        import_property_service: ImportPropertyService,
        global_id_encoder: Callable,
    ) -> None:
        self.booking_repo: BookingRepo = booking_repo()
        self.project_repo: ProjectRepo = project_repo()
        self.property_repo: PropertyRepo = property_repo()
        self.purchase_amo_matrix_repo: PurchaseAmoMatrixRepo = PurchaseAmoMatrixRepo()
        self.amocrm_class: type[AmoCRM] = amocrm_class
        self.global_id_encoder: Callable = global_id_encoder
        self.import_property_service: ImportPropertyService = import_property_service

    async def __call__(
            self,
            webhook_lead: WebhookLead,
            amo_status: Optional[AmocrmStatus],
            user_id: Optional[int],
    ) -> Booking:
        booking_purchase_data: Optional[dict] = None
        custom_fields: dict = webhook_lead.custom_fields
        project_enum: int = custom_fields.get(self.amocrm_class.project_field_id, CustomFieldValue()).enum
        project: Optional[Project] = await self.project_repo.retrieve(filters=dict(amocrm_enum=project_enum,
                                                                                   status=ProjectStatus.CURRENT))
        property_id: str = custom_fields.get(self.amocrm_class.property_field_id, CustomFieldValue()).value
        property_str_type: str = custom_fields.get(self.amocrm_class.property_str_type_field_id, CustomFieldValue()).value
        property_type: str = self.amocrm_class.property_str_type_reverse_values.get(property_str_type)
        expires_timestamp = custom_fields.get(self.amocrm_class.booking_expires_datetime_field_id)
        booking_source: BookingSource = await get_booking_source(slug=self.CREATED_SOURCE)

        purchase_type_enum: Optional[int] = custom_fields.get(
            self.amocrm_class.booking_payment_type_field_id,
            CustomFieldValue(),
        ).enum
        if purchase_type_enum and self.__is_strana_lk_2494_enable:
            purchase_amo: Optional[PurchaseAmoMatrix] = await self.purchase_amo_matrix_repo.retrieve(
                filters=dict(amo_payment_type=purchase_type_enum),
                related_fields=["mortgage_type", "payment_method"],
            )
            if not purchase_amo:
                purchase_amo: PurchaseAmoMatrix = await self.purchase_amo_matrix_repo.retrieve(
                    filters=dict(default=True),
                    related_fields=["mortgage_type", "payment_method"],
                )
            booking_purchase_data = dict(
                amo_payment_method=purchase_amo.payment_method,
                mortgage_type=purchase_amo.mortgage_type,
            ) if purchase_amo else None

        booking_data: dict = dict(
            active=True,
            amocrm_stage=self.BOOKING_STAGE,
            amocrm_substage=self.BOOKING_STAGE,
            project_id=project.id if project else None,
            amocrm_status_id=amo_status.id,
            amocrm_id=webhook_lead.lead_id,
            user_id=user_id,
            origin=f"https://{self.SITE_HOST}",
            created_source=BookingCreatedSources.AMOCRM,  # todo: deprecated
            booking_source=booking_source,
            expires=datetime.fromtimestamp(int(expires_timestamp.value))
        )

        if booking_purchase_data:
            booking_data.update(booking_purchase_data)

        if property_id and property_type:
            booking_property: Property = await self._create_property(property_id, property_type)
            booking_data.update(
                floor_id=booking_property.floor_id,
                property_id=booking_property.id,
                building_id=booking_property.building_id,
                project_id=booking_property.project_id,
            )
        booking: Booking = await self.booking_repo.create(data=booking_data)
        self.logger.warning(f"Lead {webhook_lead.lead_id} from amo was created in {__name__}")
        await booking.fetch_related("user")
        return booking

    async def _create_property(self, property_id: str, property_type: Optional[str] = None) -> Property:
        """
        Создание объекта недвижимости
        """
        global_property_type: str = self.amocrm_class.global_types_mapping.get(property_type, "GlobalFlatType")
        property_global_id: str = self.global_id_encoder(global_property_type, property_id)
        filters: dict = dict(global_id=property_global_id)
        data: dict = dict(premise=PremiseType.RESIDENTIAL, type=property_type)
        if property_type != PropertyTypes.FLAT:
            data: dict = dict(premise=PremiseType.NONRESIDENTIAL, type=property_type)
        booking_property: Property = await self.property_repo.update_or_create(filters=filters, data=data)
        await self.import_property_service(property=booking_property)
        return booking_property

    @property
    def __is_strana_lk_2494_enable(self) -> bool:
        return UnleashClient().is_enabled(FeatureFlags.strana_lk_2494)
