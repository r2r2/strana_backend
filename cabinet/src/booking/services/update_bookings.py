# pylint: disable=broad-except,too-many-statements
import re
from copy import copy
from typing import Any, Callable, Optional, Type, Union

import structlog
from tortoise.exceptions import IntegrityError

from common.amocrm import AmoCRM
from common.amocrm.repos import AmoStatusesRepo
from common.amocrm.types import AmoCustomField, AmoLead
from common.backend.models import AmocrmStatus
from common.handlers.exceptions import get_exc_info
from common.utils import partition_list
from common.unleash.client import UnleashClient
from config.feature_flags import FeatureFlags
from src.buildings.repos import Building, BuildingRepo
from src.floors.repos import Floor, FloorRepo
from src.projects.repos import Project, ProjectRepo
from src.properties.repos import Property, PropertyRepo
from src.payments.repos import PurchaseAmoMatrix, PurchaseAmoMatrixRepo

from ..constants import BookingStagesMapping, BookingSubstages
from ..event_emitter_handlers import event_emitter
from ..repos import Booking, BookingRepo
from ..types import BookingAmoCRM, BookingGraphQLRequest, BookingORM
from ...cities.repos import City, CityRepo

logger = structlog.getLogger('default')


class UpdateBookingsService:
    """
    Обновление бронирований/сделок.

    Бронирования/сделки в личном кабинете будут обновлены в соответствии с данными в AmoCRM.
    Так, будут назначены правильные ЛК-шные статусы, активность бронирований и будут обновлены
    привязки к проектам/зданиям/этажам/квартирам, если вдруг что-то изменилось.
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
    global_types_map: dict[str, str] = {
        "FLAT": "GlobalFlatType",
        "PANTRY": "GlobalPantryType",
        "PARKING": "GlobalParkingSpaceType",
        "COMMERCIAL_APARTMENT": "GlobalFlatType",
        "COMMERCIAL": "GlobalCommercialSpaceType",
    }
    related_types_mapping: dict[str, tuple[str, str]] = {
        "city": ("CityType", "id"),
        "floor": ("FloorType", "id"),
        "building": ("BuildingType", "id"),
        "project": ("GlobalProjectType", "slug"),
    }

    def __init__(
        self,
        booking_repo: Type[BookingRepo],
        amocrm_class: Type[BookingAmoCRM],
        property_repo: Type[PropertyRepo],
        global_id_encoder: Callable,
        backend_config: dict[str, Any],
        amocrm_config: dict[Any, Any],
        request_class: Type[BookingGraphQLRequest],
        floor_repo: Type[FloorRepo],
        project_repo: Type[ProjectRepo],
        cities_repo: Type[CityRepo],
        building_repo: Type[BuildingRepo],
        statuses_repo: Type[AmoStatusesRepo],
        orm_class: Optional[BookingORM] = None,
        orm_config: Optional[dict[str, Any]] = None,
    ):
        self.property_repo: PropertyRepo = property_repo()
        self.booking_repo: BookingRepo = booking_repo()
        self.amocrm_class: Type[BookingAmoCRM] = amocrm_class
        self.global_id_encoder: Callable[[str, Union[str, int]], str] = global_id_encoder
        self.request_class: Type[BookingGraphQLRequest] = request_class
        self.login: str = backend_config["internal_login"]
        self.password: str = backend_config["internal_password"]
        self.backend_url: str = backend_config["url"] + backend_config["graphql"]
        self.floor_repo: FloorRepo = floor_repo()
        self.project_repo: ProjectRepo = project_repo()
        self.cities_repo: CityRepo = cities_repo()
        self.building_repo: BuildingRepo = building_repo()
        self.statuses_repo: AmoStatusesRepo = statuses_repo()
        self.purchase_amo_matrix_repo: PurchaseAmoMatrixRepo = PurchaseAmoMatrixRepo()
        self.partition_limit: int = amocrm_config["partition_limit"]

        self.orm_class: Union[Type[BookingORM], None] = orm_class
        self.orm_config: Union[dict[str, Any], None] = copy(orm_config)
        if self.orm_config:
            self.orm_config.pop("generate_schemas", None)

    async def __call__(self):
        """
        Обновление данных бронирований из AmoCRM.

        Тут происходит изменение свойств бронирований. Когда в амо что-то там поменялось,
        у бронирований в ЛК проставятся новые свойства.

        Также столкнулись при разработке с проблемой, что некоторые тестовые бронирования в AmoCRM
        куда-то пропали - то ли были удалены, то ли ещё что-то. Решил следующим образом - если
        бронирование не было найдено в AmoCRM, то ставим его неактивным (active=False)
        и на всякий вешаем флаг "удалено в амо" (deleted_in_amo=True).
        Это нужно, чтобы не возникало ошибок, связанных с тем, что у нас в ЛК
        квартиры забронированы, а в profitbase и бэкенде - нет.
        """
        filters = dict(active=True, amocrm_id__isnull=False)
        bookings: list[Booking] = await self.booking_repo.list(filters=filters)
        booking_map: dict[int, Booking] = {b.amocrm_id: b for b in bookings}
        big_lead_ids: list[int] = [booking.amocrm_id for booking in bookings]
        properties: list[Property] = await self.property_repo.list()
        property_map: dict[str, Property] = {p.global_id: p for p in properties}

        # Сет id бронирований, что были найдены в AmoCRM
        bookings_found_in_amocrm: set[int] = set()
        async with await self.amocrm_class() as amocrm:
            for lead_ids in partition_list(big_lead_ids, self.partition_limit):
                leads = await amocrm.fetch_leads(lead_ids=lead_ids)
                for lead in leads:
                    try:
                        await self._update_lead(
                            lead=lead,
                            bookings_found_in_amocrm=bookings_found_in_amocrm,
                            booking_map=booking_map,
                            amocrm=amocrm,
                            property_map=property_map,
                        )
                    except Exception as ex:
                        logger.error('Update booking_exception', exc_info=get_exc_info(ex))

        # Деактивация и маркирование бронирований, что не были найдены в AmoCRM
        bookings_not_found_in_amocrm = set(booking_map.keys()) - bookings_found_in_amocrm
        await self.deactivate_deleted_bookings(bookings_not_found_in_amocrm)

    async def _update_lead(
        self,
        *,
        lead: AmoLead,
        bookings_found_in_amocrm: set[Any],
        booking_map: dict[int, Booking],
        amocrm: AmoCRM,
        property_map: dict[str, Property],
    ) -> None:
        """update lead"""
        bookings_found_in_amocrm.add(lead.id)

        # Не обновляем сделки из воронок, кроме городов
        if lead.pipeline_id not in amocrm.sales_pipeline_ids:
            booking = await self.booking_repo.retrieve(filters=dict(amocrm_id=lead.id))
            if booking and booking.active:
                await self.booking_repo.update(model=booking, data=dict(active=False))
            return

        booking: Booking = booking_map.get(lead.id)

        amocrm_substage: Optional[str] = amocrm.get_lead_substage(lead.status_id)
        amocrm_stage: Optional[str] = BookingStagesMapping()[amocrm_substage]
        amocrm_status: AmocrmStatus = await self.statuses_repo.retrieve(filters=dict(id=lead.status_id))

        commission_value: Optional[str] = "0"
        commission: Optional[str] = "0"
        final_payment_amount: Optional[str] = None
        price_with_sale: Optional[str] = None

        # Достаём привязку сделки из AmoCRM к квартире
        property_type: Optional[str] = None
        property_id: Optional[int] = None
        price_payed: bool = False
        booking_purchase_data: Optional[dict] = None
        lead_custom_fields: list[AmoCustomField] = lead.custom_fields_values
        for custom_field in lead_custom_fields:
            if custom_field.field_id == amocrm.property_field_id:
                property_id = int(custom_field.values[0].value)
            elif custom_field.field_id == amocrm.property_type_field_id:
                property_type: str = amocrm.property_type_reverse_values.get(
                    custom_field.values[0].enum_id
                )
            elif custom_field.field_id == amocrm.commission:
                commission = custom_field.values[0].value
            elif custom_field.field_id == amocrm.commission_value:
                commission_value = custom_field.values[0].value
            elif custom_field.field_id == amocrm.property_final_price_field_id:
                final_payment_amount = custom_field.values[0].value
            elif custom_field.field_id == amocrm.property_price_with_sale_field_id:
                price_with_sale = custom_field.values[0].value
            elif custom_field.field_id == amocrm.booking_payment_status_field_id:
                if custom_field.values[0].value in ("Да", "да", True, "true"):
                    price_payed = True
            elif custom_field.field_id == amocrm.booking_payment_type_field_id and self.__is_strana_lk_2494_enable:
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

        query_type: Optional[str] = self.types_map.get(property_type, None)
        query_name: Optional[str] = self.queries_map.get(property_type, None)
        global_type: Optional[str] = self.global_types_map.get(property_type, None)

        global_id: Optional[str] = None
        if query_type and query_name and global_type:
            global_id = self.global_id_encoder(type=global_type, id=property_id)

        # Выставляем сделку неактивной, если она невалидна
        booking_active = True
        stages_valid = self._is_stage_valid(amocrm_substage=amocrm_substage)
        if not stages_valid or lead.is_deleted:
            booking_active: bool = False

        data: dict[str, Any] = dict(
            commission=commission,
            commission_value=commission_value,
            active=booking_active,
            amocrm_status_id=lead.status_id,
            amocrm_status=amocrm_status,
            price_payed=price_payed,
        )

        if booking and booking.is_agent_assigned():
            data.pop("commission")
            data.pop("commission_value")

        if booking_purchase_data:
            data.update(booking_purchase_data)

        if final_payment_amount := final_payment_amount or price_with_sale:
            data["final_payment_amount"] = final_payment_amount
        if amocrm_stage and booking.amocrm_stage != amocrm_stage:
            data["amocrm_stage"] = amocrm_stage
        if amocrm_substage and booking.amocrm_substage != amocrm_substage:
            data["amocrm_substage"] = amocrm_substage

        old_group_status = booking.amocrm_substage if booking.amocrm_substage else None
        await self.booking_repo.update(model=booking, data=data)

        event_emitter.ee.emit(
            event='change_status',
            booking=booking,
            user=None,
            old_group_status=old_group_status,
        )
        # Если сделка находится в определённом статусе, который не требует проверки наличия квартиры
        # (Фиксация клиента за АН), то пропускаем этот шаг
        if booking.amocrm_substage in [BookingSubstages.ASSIGN_AGENT]:
            return

        _property = property_map.get(global_id)
        data = {}
        # Если у сделки назначена другая квартира или же раньше квартира не была назначена,
        # назначаем новую, предварительно импортировав
        if (global_id and not _property) or (_property and booking.property_id != _property.id):
            floor, project, building, _property = await self._import_property(
                property_id=property_id, property_type=property_type
            )
            data.update(dict(
                project=project,
                building=building,
                floor=floor,
                property=_property,
            ))
        if not property_id:
            data.update(dict(building=None, floor=None, property=None))
        await self.booking_repo.update(model=booking, data=data)

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
        if amocrm_substage in [BookingSubstages.TERMINATION, BookingSubstages.UNREALIZED]:
            return False

        return True

    async def _import_property(
        self, property_id: int, property_type: str
    ) -> Union[tuple[None, None, None, None], tuple[Floor, Project, Building, Property]]:
        """
        Импорт проекта/корпуса/этажа/квартиры с бэкенда.
        """
        floor: Optional[Floor] = None
        project: Optional[Project] = None
        building: Optional[Building] = None
        _property: Optional[Property] = None

        query_type: Optional[str] = self.types_map.get(property_type, None)
        query_name: Optional[str] = self.queries_map.get(property_type, None)
        global_type: Optional[str] = self.global_types_map.get(property_type, None)

        if query_type and query_name and global_type:
            global_id: str = self.global_id_encoder(type=global_type, id=property_id)

            request_options: dict[str, Any] = dict(
                type=query_type,
                login=self.login,
                filters=global_id,
                url=self.backend_url,
                query_name=query_name,
                password=self.password,
                query_directory=self.query_directory,
            )
            async with self.request_class(**request_options) as response:
                property_data: dict[str, Any] = response.data
                property_errors: bool = response.errors

            if not property_errors and property_data:
                floor_data: dict[str, Any] = property_data.pop("floor")

                backend_project: dict[str, Any] = property_data.pop("project")

                building_data: dict[str, Any] = property_data.pop("building")

                floor_global_id: Optional[str] = floor_data.pop("global_id", None)
                building_global_id: Optional[str] = building_data.pop("global_id", None)
                property_global_id: Optional[str] = property_data.pop("global_id", None)

                # Создаём/обновляем проект
                project_global_id_type = self.related_types_mapping["project"][0]
                project_global_id_value = backend_project.get(self.related_types_mapping["project"][1])
                project_global_id = self.global_id_encoder(project_global_id_type, project_global_id_value)

                city: Optional[City] = None
                if backend_project["city"]:
                    city: City = await self.cities_repo.retrieve(filters=dict(slug=backend_project["city"]["slug"]))
                backend_project["city"] = city

                project_filters: dict[str, Any] = dict(global_id=project_global_id)
                project: Project = await self._get_project(
                    project_filters=project_filters,
                    backend_project=backend_project,
                )

                # Создаём/обновляем корпус
                building_data["project"] = project
                property_data["project"] = project

                building_filters: dict[str, Any] = dict(global_id=building_global_id)
                building = await self.building_repo.update_or_create(
                    filters=building_filters, data=building_data
                )

                # Создаём/обновляем этаж
                floor_data["building"] = building
                property_data["building"] = building

                floor_filters: dict[str, Any] = dict(global_id=floor_global_id)
                floor = await self.floor_repo.update_or_create(
                    filters=floor_filters, data=floor_data
                )

                # Создаём/обновляем квартиру
                property_data["floor"] = floor

                property_plan: Optional[str] = property_data.get("plan")
                property_plan_png: Optional[str] = property_data.get("plan_png")

                if property_plan:
                    splat = property_plan.split("/")
                    if splat[0] in ("http:", "https:"):
                        property_plan = "/".join(splat[4:])

                if property_plan_png:
                    splat = property_plan_png.split("/")
                    if splat[0] in ("http:", "https:"):
                        property_plan_png = "/".join(splat[4:])

                property_data["plan"] = property_plan
                property_data["plan_png"] = property_plan_png

                property_data["status"] = await self._get_property_status(status=property_data["status"])

                property_filters: dict[str, Any] = dict(global_id=property_global_id)
                _property = await self.property_repo.update_or_create(filters=property_filters, data=property_data)

        return floor, project, building, _property

    async def deactivate_deleted_bookings(self, bookings_not_found_in_amocrm: set[int]) -> None:
        """Деактивация бронирований, что не были найдены в AmoCRM."""
        print("Бронирования, что не были найдены в AmoCRM:", bookings_not_found_in_amocrm)

        # amocrm_id_isnull=False Т.к. на самом первом шаге (принятие оферты),
        # создаётся бронирование, но в AmoCRM не создаётся - только при введении
        # персональных данных (следующий шаг)
        filters = dict(amocrm_id__in=bookings_not_found_in_amocrm, amocrm_id__not_isnull=True)
        data = dict(active=False, deleted_in_amo=True)
        await self.booking_repo.bulk_update(data=data, filters=filters)

    async def _get_project(self, project_filters: dict[str, Any], backend_project: dict[str, Any]) -> Project:
        backend_project.pop("global_id", None)
        backend_project.pop("id", None)

        amocrm_enum = backend_project.get("amocrm_enum")
        if isinstance(amocrm_enum, str):
            amocrm_enum = int(amocrm_enum) if amocrm_enum.isdigit() else 0
        elif not isinstance(amocrm_enum, int):
            amocrm_enum = 0

        backend_project["amocrm_enum"] = amocrm_enum
        
        project = await self.project_repo.retrieve(filters=project_filters)
        if project:
            project = await self.project_repo.update(model=project, data=backend_project)
        else:
            try:
                data: dict[str, Any] = backend_project | project_filters
                project = await self.project_repo.create(data=data)
            except IntegrityError:
                project = await self.project_repo.retrieve(filters=project_filters)

        return project

    async def _get_property_status(self, status: Optional[Union[str, int]]) -> Optional[int]:
        if status is None:
            return

        if isinstance(status, int) and 0 <= status <= 2:
            return status

        digits_match = re.search(r'\d+', str(status))

        if digits_match:
            extracted_digits = int(digits_match.group(0))
            if 0 <= extracted_digits <= 2:
                return extracted_digits

    @property
    def __is_strana_lk_2494_enable(self) -> bool:
        return UnleashClient().is_enabled(FeatureFlags.strana_lk_2494)
