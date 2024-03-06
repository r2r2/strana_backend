import structlog
from pytz import UTC
from typing import Optional, Callable, Any
from datetime import datetime, timedelta
import json

from common.amocrm.types import AmoLead
from common.profitbase import ProfitBase
from common.sentry.utils import send_sentry_log
from common.unleash.client import UnleashClient
from config.feature_flags import FeatureFlags
from config import site_config, session_config
from src.properties.repos import PropertyRepo, PropertyTypeRepo, PropertyType, Property
from src.payments.repos import PropertyPrice
from src.properties.services import ImportPropertyService, CheckProfitbasePropertyService, GetPropertyPriceService
from src.properties.exceptions import PropertyTypeMissingError, PropertyImportError
from src.users.repos import User, UserRepo
from src.booking.constants import BookingCreatedSources, BookingStages, BookingSubstages
from src.buildings.repos import (
    BuildingBookingType as BookingType,
    BuildingBookingTypeRepo as BookingTypeRepo
)
from ..entities import BaseBookingCase
from src.booking.exceptions import (
    BookingTypeMissingError,
    BookingPropertyUnavailableError,
    BookingPropertyAlreadyBookedError,
)
from ..event_emitter_handlers import event_emitter
from ..models import RequestCreateBookingModel
from src.booking.repos import Booking, BookingRepo, BookingSource, TestBookingRepo
from ..types import BookingAmoCRM
from src.task_management.services import CreateTaskInstanceService
from src.booking.utils import get_booking_source, create_lead_name, get_booking_reserv_time
from src.task_management.constants import OnlineBookingSlug
from src.task_management.utils import get_booking_tasks
from src.amocrm.repos import AmocrmStatus, AmocrmStatusRepo
from src.task_management.dto import CreateTaskDTO
from src.properties.constants import PropertyStatuses
from src.payments.repos import PurchaseAmoMatrix, PurchaseAmoMatrixRepo


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
        purchase_amo_matrix_repo: type[PurchaseAmoMatrixRepo],
        test_booking_repo: type[TestBookingRepo],
        user_repo: type[UserRepo],
        booking_type_repo: type[BookingTypeRepo],
        amocrm_class: type[BookingAmoCRM],
        profit_base_class: type[ProfitBase],
        amocrm_status_repo: type[AmocrmStatusRepo],
        create_task_instance_service: CreateTaskInstanceService,
        check_profitbase_property_service: CheckProfitbasePropertyService,
        get_property_price_service: GetPropertyPriceService,
        check_booking_task: Any,
        global_id_decoder,
    ) -> None:
        self.property_repo: PropertyRepo = property_repo()
        self.property_type_repo: PropertyTypeRepo = property_type_repo()
        self.booking_repo: BookingRepo = booking_repo()
        self.user_repo: UserRepo = user_repo()
        self.booking_type_repo: BookingTypeRepo = booking_type_repo()
        self.amocrm_status_repo: AmocrmStatusRepo = amocrm_status_repo()
        self.import_property_service: ImportPropertyService = import_property_service
        self.amocrm_class: type[BookingAmoCRM] = amocrm_class
        self.profit_base_class: type[ProfitBase] = profit_base_class
        self.global_id_decoder: Callable = global_id_decoder
        self.create_task_instance_service: CreateTaskInstanceService = create_task_instance_service
        self.check_profitbase_property_service: CheckProfitbasePropertyService = check_profitbase_property_service
        self.check_booking_task: Any = check_booking_task
        self.get_property_price_service: GetPropertyPriceService = get_property_price_service
        self.purchase_amo_matrix_repo: PurchaseAmoMatrixRepo = purchase_amo_matrix_repo()
        self.test_booking_repo: TestBookingRepo = test_booking_repo()

        self.logger: structlog.BoundLogger = structlog.get_logger(__name__)

    async def __call__(self, user_id: int, payload: RequestCreateBookingModel) -> Booking | None:
        try:
            property_type, booking_type = await self._get_property_and_booking_type(payload=payload)
        except (PropertyTypeMissingError, BookingTypeMissingError) as ex:
            sentry_ctx: dict[str, Any] = dict(
                property_slug=payload.property_slug,
                booking_type_id=payload.booking_type_id,
                property_global_id=payload.property_global_id,
                user_id=user_id,
                ex=ex,
            )
            await send_sentry_log(
                tag="CreateBookingCase",
                message="Не удалось получить тип объекта или тип бронирования",
                context=sentry_ctx,
            )
            raise ex

        property_filters: dict = dict(global_id=payload.property_global_id)
        property_data: dict = dict(property_type_id=property_type.id)  # необходимо уточнение по полям
        created_property: Property = await self.property_repo.update_or_create(
            filters=property_filters, data=property_data
        )
        is_imported, loaded_property_from_backend = await self.import_property_service(property=created_property)
        if not is_imported:
            sentry_ctx: dict[str, Any] = dict(
                is_imported=is_imported,
                loaded_property_from_backend=loaded_property_from_backend,
                created_property=created_property,
                property_data=property_data,
                ex=PropertyImportError,
            )
            await send_sentry_log(
                tag="CreateBookingCase",
                message="Не удалось импортировать объект недвижимости с портала[ImportPropertyService]",
                context=sentry_ctx,
            )
            raise PropertyImportError

        await self._check_property_in_profitbase(property_=loaded_property_from_backend)

        booking_source: BookingSource = await get_booking_source(slug=self.CREATED_SOURCE)
        booking_reserv_time: float = await get_booking_reserv_time(
            created_source=booking_source.slug,
            booking_property=loaded_property_from_backend,
        )
        user: User = await self.user_repo.retrieve(filters=dict(id=user_id))
        expires: datetime = datetime.now(tz=UTC) + timedelta(hours=booking_reserv_time)

        # booking_amocrm_id: int = await self._create_amo_lead(
        #     user=user,
        #     loaded_property=loaded_property_from_backend,
        #     booking_type=booking_type,
        # )
        #
        # await self._profitbase_booking(
        #     amocrm_id=booking_amocrm_id,
        #     property_id=self.global_id_decoder(loaded_property_from_backend.global_id)[1],
        # )
        # booking_amocrm_id: int = await self._create_amo_lead(
        #     user=user,
        #     loaded_property=loaded_property_from_backend,
        #     booking_type=booking_type,
        # )
        #
        # data: dict[str, Any] = dict(
        #     amocrm_id=booking_amocrm_id,
        #     is_test_user=user.is_test_user if user else False,
        # )
        # await self.test_booking_repo.create(data=data)
        #
        # profitbase_is_booked: bool = await self._profitbase_booking(
        #     amocrm_id=booking_amocrm_id,
        #     property_id=self.global_id_decoder(loaded_property_from_backend.global_id)[1],
        # )

        amocrm_status: AmocrmStatus = await self.amocrm_status_repo.retrieve(
            filters=dict(
                name=BookingSubstages.BOOKING_LABEL,
                pipeline_id=loaded_property_from_backend.project.amo_pipeline_id,
            ),
        )
        await loaded_property_from_backend.fetch_related("building")
        until: datetime = datetime.now(tz=UTC) + timedelta(days=booking_type.period)
        booking_data: dict = dict(
            active=True,
            # amocrm_id=booking_amocrm_id,
            amocrm_stage=self.BOOKING_STAGE,
            amocrm_substage=self.BOOKING_STAGE,
            amocrm_status=amocrm_status,
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
            should_be_deactivated_by_timer=True,
            until=until,
        )

        self.logger.info(f"{payload.payment_method_slug=}")
        self.logger.info(f"{payload.mortgage_type_by_dev=}")
        self.logger.info(f"{payload.mortgage_program_name=}")
        self.logger.info(f"{payload.calculator_options=}")

        booking_data.update(mortgage_offer=payload.mortgage_program_name)
        try:
            json.loads(payload.calculator_options)  # проверяем, что текст совместим с json
            booking_data.update(calculator_options=payload.calculator_options)
        except Exception:
            self.logger.error(
                f"В поле опции калькулятора передан не json-совместимый текст - {payload.calculator_options=}"
            )

        if payload.payment_method_slug:
            booking_property_price, price_offer_matrix = await self.get_property_price_service(
                property_id=loaded_property_from_backend.id,
                property_payment_method_slug=payload.payment_method_slug,
                property_mortgage_type_by_dev=payload.mortgage_type_by_dev,
            )
            if booking_property_price and price_offer_matrix:
                booking_data.update(
                    price_id=booking_property_price.id,
                    amo_payment_method_id=price_offer_matrix.payment_method_id,
                    mortgage_type_id=price_offer_matrix.mortgage_type_id,
                    price_offer_id=price_offer_matrix.id,
                    final_payment_amount=booking_property_price.price,
                )

        booking: Booking = await self.booking_repo.create(data=booking_data)
        event_emitter.ee.emit(event='booking_created', booking=booking, user=user)

        # находим данные из матрицы для поля в амо "Тип оплаты"
        purchase_amo: Optional[PurchaseAmoMatrix] = await self.purchase_amo_matrix_repo.list(
            filters=dict(
                payment_method_id=booking.amo_payment_method_id,
                mortgage_type_id=booking.mortgage_type_id,
            ),
            ordering="priority",
        ).first()
        payment_type_enum: Optional[int] = purchase_amo.amo_payment_type if purchase_amo else None

        booking_amocrm_id: int = await self._create_amo_lead(
            user=user,
            loaded_property=loaded_property_from_backend,
            booking_type=booking_type,
            payment_type_enum=payment_type_enum,
            booking_data=booking_data,
        )

        await self._profitbase_booking(
            amocrm_id=booking_amocrm_id,
            property_id=self.global_id_decoder(loaded_property_from_backend.global_id)[1],
        )

        await self.booking_repo.update(model=booking, data=dict(amocrm_id=booking_amocrm_id))

        # await self._process_amocrm_update_lead(
        #     booking=booking,
        #     booking_data=booking_data,
        #     payment_type_enum=payment_type_enum,
        # )

        await self.create_task_instance(booking=booking)
        await booking.fetch_related(
            "building",
            "ddu__participants",
            "project__city",
            "property__section",
            "property__property_type",
            "amocrm_status__group_status",
            "floor",
            "agent",
            "agency",
            "booking_source",
            "amo_payment_method",
            "mortgage_type",
        )
        booking.tasks = await get_booking_tasks(
            booking_id=booking.id, task_chain_slug=OnlineBookingSlug.ACCEPT_OFFER.value
        )
        self.check_booking_task.apply_async((booking.id,), eta=expires, queue="scheduled")
        return booking

    async def _create_amo_lead(
        self,
        user: User,
        loaded_property: Property,
        booking_type: BookingType,
        booking_data: dict[str, Any],
        payment_type_enum: int | None = None,
    ) -> int:
        await loaded_property.fetch_related("project__city", "property_type")
        lead_options: dict = dict(
            status=self.BOOKING_STAGE,
            city_slug=loaded_property.project.city.slug,
            property_type=loaded_property.property_type.slug,
            user_amocrm_id=user.amocrm_id,
            lead_name=create_lead_name(user),
            project_amocrm_name=loaded_property.project.amocrm_name,
            project_amocrm_enum=loaded_property.project.amocrm_enum,
            project_amocrm_organization=loaded_property.project.amocrm_organization,
            project_amocrm_pipeline_id=loaded_property.project.amo_pipeline_id,
            project_amocrm_responsible_user_id=loaded_property.project.amo_responsible_user_id,
            property_id=self.global_id_decoder(loaded_property.global_id)[1],
            booking_type_id=booking_type.amocrm_id,
            creator_user_id=user.id,
            payment_type_enum=payment_type_enum,
        )
        async with await self.amocrm_class() as amocrm:
            lead_data: list[AmoLead] = await amocrm.create_lead(**lead_options)
            lead_id: int = lead_data[0].id

            if calculator_options_data := booking_data.get("calculator_options"):
                await amocrm.send_lead_note(
                    lead_id=lead_id,
                    message=f"Выбранные опции - {calculator_options_data}",
                )
            if mortgage_offer_data := booking_data.get('mortgage_offer'):
                await amocrm.send_lead_note(
                    lead_id=lead_id,
                    message=f"Название ипотечной программы - {mortgage_offer_data}",
                )
        return lead_id

    async def _process_amocrm_update_lead(
        self,
        booking: Booking,
        booking_data: dict[str, Any],
        payment_type_enum: int | None = None,
    ) -> None:
        async with await self.amocrm_class() as amocrm:
            await amocrm.update_lead_v4(
                lead_id=booking.amocrm_id,
                payment_type_enum=payment_type_enum,
            )

            if calculator_options_data := booking_data.get("calculator_options"):
                await amocrm.send_lead_note(
                    lead_id=booking.amocrm_id,
                    message=f"Выбранные опции - {calculator_options_data}",
                )
            if mortgage_offer_data := booking_data.get('mortgage_offer'):
                await amocrm.send_lead_note(
                    lead_id=booking.amocrm_id,
                    message=f"Название ипотечной программы - {mortgage_offer_data}",
                )

    async def _check_property_in_profitbase(self, property_: Property) -> None:
        property_status, property_available = await self.check_profitbase_property_service(
            property_
        )
        property_status_free: bool = property_status == PropertyStatuses.FREE
        if not property_available or not property_status_free:
            sentry_ctx: dict[str, Any] = dict(
                property_status=property_status,
                property_available=property_available,
                property_status_free=property_status_free,
                property=property_,
                ex=BookingPropertyAlreadyBookedError,
            )
            await send_sentry_log(
                tag="CreateBookingCase",
                message=(f"CreateBookingCase: Объект недвижимости недоступен. "
                         f"booked={property_status_free}, in_deal={property_available}"),
                context=sentry_ctx,
            )
            self.logger.info(
                f"CreateBookingCase: Объект недвижимости недоступен. "
                f"booked={property_status_free}, in_deal={property_available}"
            )
            raise BookingPropertyAlreadyBookedError

    async def _profitbase_booking(self, amocrm_id: int, property_id: int) -> bool:
        """
        Бронирование в profit_base
        """
        async with await self.profit_base_class() as profit_base:
            data: dict[str, bool] = await profit_base.book_property(property_id=property_id, deal_id=amocrm_id)
            booked: bool = data.get("success", False)
            in_deal: bool = data.get("code", None) == profit_base.dealed_code
        profit_base_booked: bool = booked or in_deal
        if not profit_base_booked:
            sentry_ctx: dict[str, Any] = dict(
                data=data,
                booked=booked,
                in_deal=in_deal,
                amocrm_id=amocrm_id,
                property_id=property_id,
                ex=BookingPropertyUnavailableError,
            )
            await send_sentry_log(
                tag="CreateBookingCase",
                message=(f"CreateBookingCase: Объект недвижимости недоступен. "
                         f"booked={booked}, in_deal={in_deal}"),
                context=sentry_ctx,
            )
            await self._if_error_close_amo_lead(amocrm_id=amocrm_id)
            raise BookingPropertyUnavailableError(booked, in_deal)
        return profit_base_booked

    async def create_task_instance(self, booking: Booking) -> None:
        task_context: CreateTaskDTO = CreateTaskDTO()
        task_context.is_main = True
        await self.create_task_instance_service(booking_ids=booking.id, task_context=task_context)

    async def _get_property_and_booking_type(
        self,
        payload: RequestCreateBookingModel,
    ) -> tuple[PropertyType, BookingType]:
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
        return property_type, booking_type

    async def _if_error_close_amo_lead(self, amocrm_id: int) -> None:
        """
        В случае ошибки закрываем сделку в amoCRM
        """
        self.logger.info(f"Close amoCRM lead {amocrm_id=}")
        async with await self.amocrm_class() as amocrm:
            await amocrm.update_lead_v4(
                lead_id=amocrm_id,
                status_id=amocrm.unrealized_status_id,
            )

