from pytz import UTC
from typing import Optional, Callable
from datetime import datetime, timedelta

from common.amocrm.types import AmoLead
from common.profitbase import ProfitBase
from config import site_config, session_config
from src.properties.repos import PropertyRepo, PropertyTypeRepo, PropertyType, Property
from src.properties.services import ImportPropertyService
from src.properties.exceptions import PropertyTypeMissingError, PropertyImportError
from src.users.repos import User, UserRepo
from src.booking.constants import BookingCreatedSources, BookingStages
from src.buildings.repos import (
    BuildingBookingType as BookingType,
    BuildingBookingTypeRepo as BookingTypeRepo
)
from ..entities import BaseBookingCase
from src.booking.exceptions import BookingTypeMissingError, BookingPropertyUnavailableError
from ..models import RequestCreateBookingModel
from src.booking.repos import Booking, BookingRepo, BookingSource
from ..types import BookingAmoCRM
from src.task_management.services import CreateTaskInstanceService
from src.booking.utils import get_booking_source
from src.task_management.constants import OnlineBookingSlug
from src.task_management.utils import get_booking_tasks


class CreateBookingCase(BaseBookingCase):
    """
    Кейс создания сделки
    """
    CREATED_SOURCE: str = BookingCreatedSources.LK
    BOOKING_STAGE: str = BookingStages.BOOKING
    SITE_HOST: str = site_config["site_host"]
    DOCUMENT_KEY: str = session_config["document_key"]

    def __init__(
        self,
        import_property_service: ImportPropertyService,
        property_repo: type[PropertyRepo],
        property_type_repo: type[PropertyTypeRepo],
        booking_repo: type[BookingRepo],
        user_repo: type[UserRepo],
        booking_type_repo: type[BookingTypeRepo],
        amocrm_class: type[BookingAmoCRM],
        profit_base_class: type[ProfitBase],
        create_task_instance_service: CreateTaskInstanceService,
        get_booking_reserv_time,
        global_id_decoder,
    ) -> None:
        self.property_repo: PropertyRepo = property_repo()
        self.property_type_repo: PropertyTypeRepo = property_type_repo()
        self.booking_repo: BookingRepo = booking_repo()
        self.user_repo: UserRepo = user_repo()
        self.booking_type_repo: BookingTypeRepo = booking_type_repo()
        self.import_property_service: ImportPropertyService = import_property_service
        self.amocrm_class: type[BookingAmoCRM] = amocrm_class
        self.profit_base_class: type[ProfitBase] = profit_base_class
        self.get_booking_reserv_time: Callable = get_booking_reserv_time
        self.global_id_decoder: Callable = global_id_decoder
        self.create_task_instance_service: CreateTaskInstanceService = create_task_instance_service

    async def __call__(self, user_id: int, payload: RequestCreateBookingModel) -> Booking | None:
        property_type: Optional[PropertyType] = await self.property_type_repo.retrieve(
            filters=dict(slug=payload.property_slug, is_active=True)
        )
        if not property_type:
            raise PropertyTypeMissingError

        booking_type: Optional[BookingType] = await self.booking_type_repo.retrieve(
            filters=dict(id=payload.booking_type_id)
        )
        if not booking_type:
            raise BookingTypeMissingError

        property_filters: dict = dict(global_id=payload.property_global_id)
        property_data: dict = dict(property_type_id=property_type.id)  # необходимо уточнение по полям
        created_property: Property = await self.property_repo.update_or_create(
            filters=property_filters, data=property_data
        )
        is_imported, loaded_property_from_backend = await self.import_property_service(property=created_property)
        if not is_imported:
            raise PropertyImportError

        booking_source: BookingSource = await get_booking_source(slug=self.CREATED_SOURCE)

        booking_reserv_time: float = await self.get_booking_reserv_time(
            created_source=self.CREATED_SOURCE,
            booking_property=loaded_property_from_backend,
        )
        user: User = await self.user_repo.retrieve(filters=dict(id=user_id))
        expires: datetime = datetime.now(tz=UTC) + timedelta(hours=booking_reserv_time)
        booking_amocrm_id: int = await self._create_amo_lead(
            user=user,
            loaded_property=loaded_property_from_backend,
            booking_type=booking_type,
        )
        profit_base_is_booked: bool = await self._profit_base_booking(
            amocrm_id=booking_amocrm_id, property_id=self.global_id_decoder(loaded_property_from_backend.global_id)[1]
        )

        booking_data: dict = dict(
            acitve=True,
            amocrm_id=booking_amocrm_id,
            amocrm_stage=self.BOOKING_STAGE,
            amocrm_substage=self.BOOKING_STAGE,
            user_id=user_id,
            origin=f"https://{self.SITE_HOST}",
            created_source=self.CREATED_SOURCE,  # todo: deprecated
            booking_source=booking_source,
            expires=expires,
            booking_period=booking_type.period,
            floor_id=loaded_property_from_backend.floor_id,
            property_id=loaded_property_from_backend.id,
            building_id=loaded_property_from_backend.building_id,
            project_id=loaded_property_from_backend.project_id,
            payment_amount=booking_type.price,
        )

        if profit_base_is_booked:
            booking: Booking = await self.booking_repo.create(data=booking_data)
            await self.create_task_instance(booking=booking)
            booking.tasks = await get_booking_tasks(
                booking_id=booking.id, task_chain_slug=OnlineBookingSlug.ACCEPT_OFFER.value
            )
            return booking

    async def _create_amo_lead(
            self,
            user: User,
            loaded_property: Property,
            booking_type: BookingType,
    ) -> int:
        await loaded_property.fetch_related("project__city", "property_type")
        lead_options: dict = dict(
            status=self.BOOKING_STAGE,
            city_slug=loaded_property.project.city.slug,
            property_type=loaded_property.property_type.slug,
            user_amocrm_id=user.amocrm_id,
            project_amocrm_name=loaded_property.project.amocrm_name,
            project_amocrm_enum=loaded_property.project.amocrm_enum,
            project_amocrm_organization=loaded_property.project.amocrm_organization,
            project_amocrm_pipeline_id=loaded_property.project.amo_pipeline_id,
            project_amocrm_responsible_user_id=loaded_property.project.amo_responsible_user_id,
            property_id=self.global_id_decoder(loaded_property.global_id)[1],
            booking_type_id=booking_type.amocrm_id,
            creator_user_id=user.id,
        )
        async with await self.amocrm_class() as amocrm:
            lead_data: list[AmoLead] = await amocrm.create_lead(**lead_options)
            lead_id: int = lead_data[0].id
        return lead_id

    async def _profit_base_booking(self, amocrm_id: int, property_id: int) -> bool:
        """
        Бронирование в profit_base
        """
        async with await self.profit_base_class() as profit_base:
            data: dict[str, bool] = await profit_base.book_property(property_id=property_id, deal_id=amocrm_id)
            booked: bool = data.get("success", False)
            in_deal: bool = data.get("code", None) == profit_base.dealed_code
        profit_base_booked: bool = booked or in_deal
        if not profit_base_booked:
            raise BookingPropertyUnavailableError(booked, in_deal)
        return profit_base_booked

    async def create_task_instance(self, booking: Booking) -> None:
        await self.create_task_instance_service(booking_ids=booking.id)
