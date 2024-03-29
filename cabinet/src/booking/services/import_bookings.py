# pylint: disable=too-many-statements
# pylint: disable=arguments-differ
import structlog
from copy import copy
from datetime import datetime
from typing import Any, Callable, Optional, Type, Union
from enum import IntEnum
from pytz import UTC

from tortoise.queryset import QuerySet

from common.amocrm import AmoCRM
from common.amocrm.constants import AmoContactQueryWith, AmoLeadQueryWith
from common.amocrm.repos import AmoStatusesRepo
from common.amocrm.types import AmoContact, AmoCustomField, AmoLead
from common.backend.models import AmocrmStatus
from common.utils import partition_list
from common.unleash.client import UnleashClient
from config.feature_flags import FeatureFlags
from src.amocrm.repos import AmocrmStatusRepo
from src.agents.repos import AgentRepo
from src.booking.loggers.wrappers import booking_changes_logger
from src.booking.constants import BookingCreatedSources
from src.buildings.repos import Building, BuildingRepo
from src.floors.repos import FloorRepo
from src.projects.repos import ProjectRepo, Project
from src.properties.constants import PremiseType, PropertyTypes
from src.properties.repos import Property, PropertyRepo
from src.properties.services import ImportPropertyService
from src.users.loggers.wrappers import user_changes_logger
from src.users.repos import User, UserRepo
from src.task_management.constants import FixationExtensionSlug, BOOKING_UPDATE_FIXATION_STATUSES
from src.projects.constants import ProjectStatus
from src.payments.repos import PurchaseAmoMatrix, PurchaseAmoMatrixRepo

from ..constants import BookingStagesMapping, BookingSubstages
from ..entities import BaseBookingService
from ..event_emitter_handlers import event_emitter
from ..mixins import BookingLogMixin
from src.booking.repos import Booking, BookingRepo, BookingSource
from ..types import BookingGraphQLRequest, BookingORM
from src.booking.utils import get_booking_source


class LeadStatuses(IntEnum):
    """
     Статусы закрытых сделок в амо.
    """
    REALIZED: int = 142  # Успешно реализовано
    UNREALIZED: int = 143  # Закрыто и не реализовано


class ImportBookingsService(BaseBookingService, BookingLogMixin):
    """
    Импорт бронирований из АМО
    """

    query_directory: str = "/src/booking/queries/"
    queries_map: dict[str, str] = {
        "FLAT": "globalFlat.graphql",
        "PANTRY": "globalPantry.graphql",
        "PARKING": "globalParking.graphql",
        "COMMERCIAL": "globalCommercial.graphql",
        "COMMERCIAL_APARTMENT": "globalCommercialApartment.graphql",
    }
    types_map: dict[str, str] = {
        "FLAT": "globalFlat",
        "PANTRY": "globalPantry",
        "PARKING": "globalParking",
        "COMMERCIAL_APARTMENT": "globalFlat",
        "COMMERCIAL": "globalCommercialSpace",
    }

    def __init__(
        self,
        user_types: Any,
        backend_config: dict[str, Any],
        booking_repo: Type[BookingRepo],
        user_repo: Type[UserRepo],
        agent_repo: Type[AgentRepo],
        amocrm_status_repo: Type[AmocrmStatusRepo],
        update_task_instance_status_task: Any,
        amocrm_class: Type[AmoCRM],
        floor_repo: Type[FloorRepo],
        project_repo: Type[ProjectRepo],
        property_repo: Type[PropertyRepo],
        building_repo: Type[BuildingRepo],
        statuses_repo: Type[AmoStatusesRepo],
        request_class: Type[BookingGraphQLRequest],
        import_property_service: ImportPropertyService,
        amocrm_config: dict[Any, Any],
        global_id_encoder: Callable,
        check_pinning: Optional[Any] = None,
        orm_class: Optional[BookingORM] = None,
        orm_config: Optional[dict[str, Any]] = None,
        create_booking_log_task: Optional[Any] = None,
        check_booking_task: Optional[Any] = None,

        logger=structlog.getLogger(__name__),
    ) -> None:
        self.logger = logger
        self.user_repo: UserRepo = user_repo()
        self.booking_repo: BookingRepo = booking_repo()
        self.floor_repo: FloorRepo = floor_repo()
        self.agent_repo: AgentRepo = agent_repo()
        self.project_repo: ProjectRepo = project_repo()
        self.property_repo: PropertyRepo = property_repo()
        self.building_repo: BuildingRepo = building_repo()
        self.statuses_repo: AmoStatusesRepo = statuses_repo()
        self.import_property_service: ImportPropertyService = import_property_service
        self.check_pinning = check_pinning
        self.amocrm_status_repo: AmocrmStatusRepo = amocrm_status_repo()
        self.purchase_amo_matrix_repo: PurchaseAmoMatrixRepo = PurchaseAmoMatrixRepo()
        self.update_task_instance_status_task = update_task_instance_status_task
        self.user_update = user_changes_logger(
            self.user_repo.update, self, content="Импорт бронирований из АМО"
        )

        self.user_types: Any = user_types
        self.amocrm_class: Type[AmoCRM] = amocrm_class
        self.create_booking_log_task: Any = create_booking_log_task
        self.request_class: Type[BookingGraphQLRequest] = request_class
        self.global_id_encoder: Callable = global_id_encoder

        self.login: str = backend_config["internal_login"]
        self.password: str = backend_config["internal_password"]
        self.backend_url: str = backend_config["url"] + backend_config["graphql"]

        self.partition_limit: int = amocrm_config["partition_limit"]
        self.orm_class: Union[Type[BookingORM], None] = orm_class
        self.orm_config: Union[dict[str, Any], None] = copy(orm_config)
        if self.orm_config:
            self.orm_config.pop("generate_schemas", None)
        self.booking_update = booking_changes_logger(
            self.booking_repo.update, self, content="Подписание ДДУ",
        )
        self.check_booking_task: Any = check_booking_task

    async def __call__(self, user_id: int) -> bool:
        if self.__is_strana_lk_3412_enable():
            self.logger.debug(f"3412 Запуск импорта сделок для пользователя {user_id}")
        user_filters: dict[str, Any] = dict(id=user_id)
        user: User = await self.user_repo.retrieve(filters=user_filters, related_fields=["agent"])
        q_filters = [self.agent_repo.q_builder(
            or_filters=[
                dict(
                    is_active=True,
                    is_approved=True,
                    is_deleted=False,
                    amocrm_id__isnull=False,
                    type=self.user_types.AGENT,
                ),
                dict(
                    is_deleted=False,
                    amocrm_id__isnull=False,
                    type=self.user_types.REPRES,
                ),
            ]
        )]
        agents: list[User] = await self.agent_repo.list(q_filters=q_filters)
        self.logger.info(f"Найдено агентов в базе по условиям, в количестве - {len(agents)} шт.")

        async with await self.amocrm_class() as amocrm:
            import_contact: Optional[AmoContact] = await amocrm.fetch_contact(
                user_id=user.amocrm_id,
                query_with=[AmoContactQueryWith.leads]
            )
            bookings: QuerySet = self.booking_repo.list()
            booking_ids: list[int] = await bookings.distinct().values_list("amocrm_id", flat=True)

            if self.__is_strana_lk_3412_enable():
                self.logger.debug(f"3412 Контакт клиента из АМО {import_contact}")
                self.logger.debug(f"3412 Список amocrm_id для обновления {booking_ids=}")
                self.logger.debug(f"3412 len {len(booking_ids)}")

            counter_updated_leads = 0
            if import_contact:
                big_lead_ids: list[int] = [lead.id for lead in import_contact.embedded.leads]
                for lead_ids in partition_list(big_lead_ids, self.partition_limit):
                    if lead_ids:
                        leads: list[AmoLead] = await amocrm.fetch_leads(
                            lead_ids=lead_ids,
                            query_with=[AmoLeadQueryWith.contacts],
                        )
                        self.logger.info(f"Для клиента {user.id=} найдено сделок, в количестве - {len(leads)} шт.")
                        for lead in leads:
                            self.logger.info(f"Для клиента {user.id=} инициирован импорт сделки с {lead.id=}")
                            counter_updated_leads += 1
                            await self._update_lead(
                                lead=lead,
                                booking_ids=booking_ids,
                                amocrm=amocrm,
                                user=user,
                                agents=agents,
                            )

            if self.__is_strana_lk_3412_enable():
                self.logger.debug(f"3412 Обновлено {counter_updated_leads} сделок")

        data: dict[str, Any] = dict(is_imported=True)
        await self.user_update(user=user, data=data)
        if self.check_pinning is not None:
            self.check_pinning.as_task(user_id=user.id)
        return True

    async def _update_lead(
        self,
        lead: AmoLead,
        booking_ids: list[int],
        amocrm: AmoCRM,
        user: User,
        agents: list[User],
    ) -> None:
        """
        Update lead
        """
        booking: Optional[Booking] = None
        booking_purchase_data: Optional[dict] = None
        if lead.id in booking_ids:
            self.logger.info(f"Сделка с {lead.id=} существует в базе")
            booking = await self.booking_repo.retrieve(filters=dict(amocrm_id=lead.id))

        # Не импортируем сделки из воронок, кроме городов
        if lead.pipeline_id not in amocrm.sales_pipeline_ids:
            self.logger.info(f"Сделка с {lead.id=} не в воронке городов")
            if booking and booking.active:
                await self.booking_update(booking=booking, data=dict(active=False))
            return

        if lead.is_deleted:
            self.logger.info(f"Сделка с {lead.id=} отмечена как удаленная в АМО")
            if booking and not booking.deleted_in_amo:
                await self.booking_update(booking=booking, data=dict(deleted_in_amo=True))
            return

        # Импорт сделки из амо в БД - далее импортируются поля сделки из амо в БД
        amocrm_substage: str = amocrm.get_lead_substage(lead.status_id)
        amocrm_stage: str = BookingStagesMapping()[amocrm_substage]
        amocrm_status: AmocrmStatus = await self.statuses_repo.retrieve(
            filters=dict(id=lead.status_id)
        )
        amocrm_cabinet_status = await self.amocrm_status_repo.retrieve(
            filters=dict(id=amocrm_status.id if amocrm_status else None),
            related_fields=["group_status"],
        )

        if amocrm_cabinet_status is None:
            self.logger.error(f"3412 amocrm_cabinet_status для {amocrm_status} не найден")

        if (
            booking and
            amocrm_cabinet_status.group_status
            and amocrm_cabinet_status.group_status.name not in BOOKING_UPDATE_FIXATION_STATUSES
        ):
            self.update_task_instance_status_task.delay(
                booking_id=booking.id,
                status_slug=FixationExtensionSlug.DEAL_ALREADY_BOOKED.value,
                caller_info=self.__class__.__name__,
            )

        property_id: Optional[int] = None
        property_type: Optional[str] = None
        property_str_type: Optional[str] = None
        price_payed: bool = False
        bill_paid: bool = False
        commission_value: Optional[str] = "0"
        commission: Optional[str] = "0"

        lead_until: Optional[str] = None
        lead_expires: Optional[datetime] = None
        lead_booking_price: Optional[str] = None
        lead_booking_final_price: Optional[str] = None
        lead_booking_price_with_sale: Optional[str] = None
        lead_project_enum: Optional[int] = None
        lead_created: int = lead.created_at
        if not lead.custom_fields_values:
            self.logger.error("Booking fatal error")
            return

        for custom_field in lead.custom_fields_values:
            custom_field: AmoCustomField
            if custom_field.field_id == amocrm.property_field_id:
                property_id = int(custom_field.values[0].value)
            if custom_field.field_id == amocrm.property_type_field_id:
                property_type = amocrm.property_type_reverse_values[
                    custom_field.values[0].enum_id
                ]
            if custom_field.field_id == amocrm.property_str_type_field_id:
                property_str_type = amocrm.property_str_type_reverse_values[
                    custom_field.values[0].value
                ]
            if custom_field.field_id == amocrm.booking_payment_status_field_id:
                if custom_field.values[0].value in ("Да", "да", True, "true"):
                    price_payed = True
            if custom_field.field_id == amocrm.booking_bill_paid_field_id:
                if custom_field.values[0].value in ("Да", "да", True, "true"):
                    bill_paid = True
            elif custom_field.field_id == amocrm.commission:
                commission = custom_field.values[0].value
            elif custom_field.field_id == amocrm.commission_value:
                commission_value = custom_field.values[0].value
            if custom_field.field_id == amocrm.booking_end_field_id:
                lead_until = custom_field.values[0].value
            if custom_field.field_id == amocrm.booking_price_field_id:
                lead_booking_price = custom_field.values[0].value
            if custom_field.field_id == amocrm.property_final_price_field_id:
                lead_booking_final_price = custom_field.values[0].value
            if custom_field.field_id == amocrm.property_price_with_sale_field_id:
                lead_booking_price_with_sale = custom_field.values[0].value
            if custom_field.field_id == amocrm.booking_expires_datetime_field_id:
                lead_expires_amo_timestamp = custom_field.values[0].value
                lead_expires: datetime = datetime.fromtimestamp(lead_expires_amo_timestamp, tz=UTC)
            if custom_field.field_id == amocrm.project_field_id:
                lead_project_enum: int = custom_field.values[0].enum_id
            if custom_field.field_id == amocrm.booking_payment_type_field_id and self.__is_strana_lk_2494_enable:
                purchase_type_enum: Optional[int] = custom_field.values[0].enum_id
                if purchase_type_enum:
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

        property_type: str = property_type or property_str_type
        if property_id and property_type:
            booking_property = await self._import_property(
                property_id=property_id, property_type=property_type
            )
        else:
            booking_property = None

        building: Optional[Building] = booking_property.building if booking_property else None

        booking_active: bool = True
        booking_amocrm_id: int = lead.id
        booking_stage: str = amocrm_stage
        booking_substage: str = amocrm_substage
        booking_price_payed: bool = price_payed
        booking_bill_payed: bool = bill_paid
        booking_payment_amount: Optional[int] = lead_booking_price or booking.payment_amount if booking else None
        booking_final_payment_amount: Optional[int] = lead_booking_final_price or lead_booking_price_with_sale
        booking_created: datetime = datetime.fromtimestamp(int(lead_created), tz=UTC)
        booking_expires: datetime = lead_expires
        booking_until: Optional[datetime] = (
            datetime.fromtimestamp(int(lead_until)) if lead_until else booking.until if booking else None
        )

        project = None
        if lead_project_enum:
            project: Optional[Project] = await self.project_repo.retrieve(filters=dict(amocrm_enum=lead_project_enum,
                                                                                       status=ProjectStatus.CURRENT))

        stages_valid: bool = self._is_stage_valid(amocrm_substage=amocrm_substage)
        if not stages_valid:
            booking_active = False

        filters: dict[str, Any] = dict(amocrm_id=booking_amocrm_id)

        data: dict[str, Any] = dict(
            user=user,
            floor=booking_property.floor if booking_property else None,
            project=project,
            building=booking_property.building if booking_property else None,
            property=booking_property,
            until=booking_until,
            expires=booking_expires,
            active=booking_active,
            profitbase_booked=True,
            created=booking_created,
            amocrm_stage=booking_stage,
            price_payed=booking_price_payed,
            bill_paid=booking_bill_payed,
            amocrm_substage=booking_substage,
            payment_amount=booking_payment_amount,
            final_payment_amount=booking_final_payment_amount,
            start_commission=building.default_commission if building else None,
            commission=commission,
            commission_value=commission_value,
            amocrm_status_id=lead.status_id,
            amocrm_status=amocrm_status,
        )

        if booking_purchase_data:
            data.update(booking_purchase_data)

        if booking and booking.is_agent_assigned():
            data.pop("commission")
            data.pop("commission_value")

        lead_contacts: set[int] = {contact.id for contact in lead.embedded.contacts}
        self.logger.info(f"Контакты сделки с {lead.id=}: {lead_contacts=}")
        self.logger.info(f"Статус сделки с {lead.id=}: {lead.status_id=}")
        self.logger.info(f"Пересечение контактов сделки с {lead.id=} с контактами брокеров по условиям в базе:"
                         f" {lead_contacts.intersection(set(agent.amocrm_id for agent in agents))}")
        self.logger.info(f"Агент клиента {user.id=}: {user.agent_id=}")
        self.logger.info(f"Агент клиента {user.id=} есть в базе (с условиями):"
                         f" {user.agent_id in [agent.id for agent in agents]}")

        # Не перепривязываем закрытые сделки других агентов у клиента
        if lead.status_id not in (LeadStatuses.REALIZED, LeadStatuses.UNREALIZED) and (
            lead_contacts.intersection(set(agent.amocrm_id for agent in agents)) and user.agent_id
        ):
            data.update(dict(agent_id=user.agent_id, agency_id=user.agency_id))
        else:
            if self.__is_strana_lk_3412_enable():
                self.logger.debug(f"3412 Не перепривязываем закрытую сделку {lead.id} других агентов у клиента ")
                self.logger.debug(f"3412 {lead_contacts} {agents} {user.agent_id} ")

        booking = await self.booking_repo.retrieve(filters=filters)
        if booking:
            if self.__is_strana_lk_3412_enable():
                self.logger.debug(f"3412 Сделка по фильтру найдена и будет обновлена")
            await self.booking_repo.update(model=booking, data=data)
        else:
            if self.__is_strana_lk_3412_enable():
                self.logger.debug(f"3412 Сделка по фильтру {filters=} не найдена и будет создана")
                data.update(
                    agent_id=user.agent_id,
                    agency_id=user.agency_id,
                )
            booking_source: BookingSource = await get_booking_source(slug=BookingCreatedSources.AMOCRM)
            data.update(
                amocrm_id=lead.id,
                created_source=BookingCreatedSources.AMOCRM,  # todo: deprecated
                booking_source=booking_source,
            )
            booking: Booking = await self.booking_repo.create(data=data)
            event_emitter.ee.emit(event='booking_created', booking=booking)

            self.check_booking_task.apply_async((booking.id,), eta=booking.expires, queue="scheduled") 

    @staticmethod
    def _is_stage_valid(amocrm_substage: str) -> bool:
        """Считаем ли мы сделку из AmoCRM валидной.

        Валидной считается сделка, у которой есть привязка к квартире.
        Такие сделки имеют, как минимум, статус "Бронь".

        У валидных сделок забронированы/проданы квартиры в profitbase.
        """
        # Если стадия бронирования из AmoCRM не участвует в логике ЛК, сделка невалидна
        # (например, "Принимают решение", "Назначить встречу" или "Первичный контакт")
        if amocrm_substage is None:
            return False

        # Сделка невалидна, если в AmoCRM статус "Закрыто и не реализовано" или "Расторжение"
        if amocrm_substage in [BookingSubstages.TERMINATION,
                               BookingSubstages.UNREALIZED,
                               BookingSubstages.MAKE_DECISION]:
            return False

        return True

    async def _import_property(
        self, property_id: int, property_type: str
    ) -> Optional[Property]:
        """
        Импорт проекта/корпуса/этажа/квартиры с бэкенда.
        """
        global_property_type: str = self.amocrm_class.global_types_mapping[property_type]
        property_global_id: str = self.global_id_encoder(
            global_property_type, property_id
        )

        filters: dict[str, Any] = dict(global_id=property_global_id)
        data: dict[str, Any] = dict(premise=PremiseType.RESIDENTIAL, type=property_type)
        if property_type != PropertyTypes.FLAT:
            data: dict[str, Any] = dict(premise=PremiseType.NONRESIDENTIAL, type=property_type)
        booking_property: Property = await self.property_repo.update_or_create(
            filters=filters, data=data)
        await self.import_property_service(property=booking_property)
        return booking_property

    @property
    def __is_strana_lk_2494_enable(self) -> bool:
        return UnleashClient().is_enabled(FeatureFlags.strana_lk_2494)

    def __is_strana_lk_3412_enable(self) -> bool:
        return UnleashClient().is_enabled(FeatureFlags.strana_lk_3412)
