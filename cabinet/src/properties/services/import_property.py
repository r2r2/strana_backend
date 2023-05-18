# pylint: disable=protected-access,broad-except,redefined-builtin
from copy import copy
from typing import Any, Callable, Optional, Type, Union

from pypika.queries import Selectable
from tortoise.expressions import Subquery
from tortoise.functions import F

from common.backend.models import (
    BackendBuilding, BackendCity, BackendFloor,
    BackendProject, BackendProperty, BackendSection,
    BackendSpecialOfferProperty
)
from common.backend.repos import (
    BackendBuildingBookingTypesRepo, BackendFloorsRepo,
    BackendPropertiesRepo, BackendSectionsRepo,
    BackendSpecialOfferRepo
)
from src.buildings.repos import BuildingBookingType, BuildingBookingTypeRepo
from src.cities.repos import City, CityRepo
from src.properties.constants import PropertyStatuses
from .import_building_booking_types import ImportBuildingBookingTypesService
from ..entities import BasePropertyService
from ..repos import Property, PropertyRepo
from ..types import PropertyBuildingRepo, PropertyFloorRepo, PropertyORM, PropertyProjectRepo


class ImportPropertyService(BasePropertyService):
    """
    Импорт объекта недвижимости с бэкенда
    """

    property_types_mapping: dict[str, Any] = {
        "flat": "GlobalFlatType",
        "pantry": "GlobalPantryType",
        "parking": "GlobalParkingSpaceType",
        "commercial": "GlobalCommercialSpaceType",
        "commercial_apartment": "GlobalFlatType",
    }
    related_types_mapping: dict[str, Any] = {
        "city": ("CityType", "id"),
        "floor": ("FloorType", "id"),
        "building": ("BuildingType", "id"),
        "project": ("GlobalProjectType", "slug"),
    }

    def __init__(
        self,
        property_repo: Type[PropertyRepo],
        floor_repo: Type[PropertyFloorRepo],
        project_repo: Type[PropertyProjectRepo],
        building_repo: Type[PropertyBuildingRepo],
        building_booking_type_repo: Type[BuildingBookingTypeRepo],
        backend_building_booking_type_repo: Type[BackendBuildingBookingTypesRepo],
        backend_properties_repo: Type[BackendPropertiesRepo],
        backend_floors_repo: Type[BackendFloorsRepo],
        backend_sections_repo: Type[BackendSectionsRepo],
        global_id_encoder: Callable[[str, str], str],
        global_id_decoder: Callable[[str], list[str]],
        orm_class: Optional[Type[PropertyORM]] = None,
        orm_config: Optional[dict[str, Any]] = None,
        import_building_booking_types_service: Optional[ImportBuildingBookingTypesService] = None,
        backend_special_offers_repo: Optional[Type[BackendSpecialOfferRepo]] = None,
    ) -> None:
        self.floor_repo: PropertyFloorRepo = floor_repo()
        self.property_repo: PropertyRepo = property_repo()
        self.project_repo: PropertyProjectRepo = project_repo()
        self.city_repo: CityRepo = CityRepo()
        self.building_repo: PropertyBuildingRepo = building_repo()
        self.building_booking_type_repo: BuildingBookingTypeRepo = building_booking_type_repo()
        self.backend_building_booking_type_repo: BackendBuildingBookingTypesRepo = backend_building_booking_type_repo()
        self.backend_properties_repo: BackendPropertiesRepo = backend_properties_repo()
        self.backend_floors_repo: BackendFloorsRepo = backend_floors_repo()
        self.backend_sections_repo: BackendSectionsRepo = backend_sections_repo()
        self.import_building_booking_types_service = import_building_booking_types_service
        if backend_special_offers_repo:
            self.backend_special_offers_repo: BackendSpecialOfferRepo = backend_special_offers_repo()
        else:
            self.backend_special_offers_repo = None

        self.global_id_encoder: Callable[[str, str], str] = global_id_encoder
        self.global_id_decoder: Callable[[str], list[str]] = global_id_decoder

        self.orm_class: Union[Type[PropertyORM], None] = orm_class
        self.orm_config: Union[dict[str, Any], None] = copy(orm_config)
        if self.orm_config:
            self.orm_config.pop("generate_schemas", None)

    async def __call__(
        self, property_id: Optional[int] = None, property: Optional[Property] = None
    ) -> tuple[bool, Property]:
        if not property:
            filters: dict[str, Any] = dict(id=property_id)
            property: Property = await self.property_repo.retrieve(filters=filters)
        status: bool = True

        if not property.global_id:
            return status, property

        backend_property_id = self.global_id_decoder(property.global_id)[1]
        backend_property = await self._load_property_from_backend(backend_property_id)
        if backend_property is None:
            return False, property

        backend_project: BackendProject = backend_property.project
        backend_city: BackendCity = backend_project.city
        backend_floor: BackendFloor = backend_property.floor
        backend_building: BackendBuilding = backend_property.building

        # Создаём/обновляем проект
        city: City = await self.city_repo.retrieve(filters=dict(slug=backend_city.slug))
        project_global_id_type = self.related_types_mapping["project"][0]
        project_global_id_value = getattr(backend_project, self.related_types_mapping["project"][1], None)
        project_global_id = self.global_id_encoder(project_global_id_type, project_global_id_value)
        project_data = dict(
            name=backend_project.name,
            slug=backend_project.slug,
            amocrm_name=backend_project.amocrm_name,
            amocrm_enum=backend_project.amocrm_enum,
            amocrm_organization=backend_project.amocrm_organization,
            amo_pipeline_id=backend_project.amo_pipeline_id,
            amo_responsible_user_id=backend_project.amo_responsible_user_id,
            city=city,
            is_active=backend_project.active,
            status=backend_project.status
        )
        project = await self.project_repo.update_or_create(
            filters=dict(global_id=project_global_id), data=project_data
        )

        # Создаём/обновляем корпус
        building_global_id_type = self.related_types_mapping["building"][0]
        building_global_id_value = getattr(
            backend_building, self.related_types_mapping["building"][1], None
        )

        building_global_id = self.global_id_encoder(
            building_global_id_type, building_global_id_value
        )
        building_data = dict(
            name=backend_building.name,
            address=backend_building.address,
            ready_quarter=backend_building.ready_quarter,
            built_year=backend_building.built_year,
            booking_active=backend_building.booking_active,
            booking_period=backend_building.booking_period,
            booking_price=backend_building.booking_price,
            total_floor=backend_property.total_floors,
            project=project,
        )
        building = await self.building_repo.update_or_create(
            filters=dict(global_id=building_global_id), data=building_data
        )

        # Создаём/обновляем типы бронирования у корпуса,
        # а также удаляем отвязанные от корпуса типы бронирования
        building_booking_types = await building.booking_types
        used_building_booking_type_ids: list[int] = await self.backend_building_booking_type_repo.list().\
            distinct().values_list('id', flat=True)
        filters = dict(id__in=used_building_booking_type_ids)
        created_or_updated_booking_types: list[BuildingBookingType] = \
            await self.building_booking_type_repo.list(filters=filters)
        if created_or_updated_booking_types:
            await building.booking_types.add(*created_or_updated_booking_types)

        booking_types_for_unlinking: list[BuildingBookingType] = []
        for booking_type in building_booking_types:
            if booking_type.pk not in used_building_booking_type_ids:
                booking_types_for_unlinking.append(booking_type)
        if booking_types_for_unlinking:
            await building.booking_types.remove(*booking_types_for_unlinking)

        # Создаём/обновляем этаж
        floor_global_id_type = self.related_types_mapping["floor"][0]
        floor_global_id_value = getattr(backend_floor, self.related_types_mapping["floor"][1], None)
        floor_global_id = self.global_id_encoder(floor_global_id_type, floor_global_id_value)
        floor_data = dict(number=backend_floor.number, building=building)
        floor = await self.floor_repo.update_or_create(filters=dict(global_id=floor_global_id), data=floor_data)

        # Создаём/обновляем квартиру
        property_global_id_type = self.property_types_mapping[backend_property.type]
        property_global_id_value = str(backend_property.id)
        property_global_id = self.global_id_encoder(
            property_global_id_type, property_global_id_value
        )

        # Получаем данные по похожему объекту недвижимости
        if self.backend_special_offers_repo:
            similar_property = await self._get_similar_property_from_backend(backend_property)
            if similar_property:
                similar_property_global_id_type = self.property_types_mapping[similar_property.type]
                similar_property_global_id_value = str(similar_property.id)
                similar_property_global_id = self.global_id_encoder(
                    similar_property_global_id_type, similar_property_global_id_value
                )
            else:
                similar_property_global_id = None
            # Получаем данные по акциям для объекта недвижимости
            special_offers = await self._get_special_offers_from_backend(backend_property.id)
        else:
            similar_property_global_id = None
            special_offers = None

        property_data = dict(
            global_id=property_global_id,
            article=backend_property.article,
            plan=backend_property.plan,
            plan_png=backend_property.plan_png,
            price=backend_property.price,
            original_price=backend_property.original_price,
            final_price=backend_property.price,
            area=backend_property.area,
            action=backend_property.action,
            status=backend_property.status,
            rooms=backend_property.rooms,
            number=backend_property.number,
            maternal_capital=backend_property.maternal_capital,
            preferential_mortgage=backend_property.preferential_mortgage,
            project=project,
            building=building,
            floor=floor,
            similar_property_global_id=similar_property_global_id,
            special_offers=special_offers,
            total_floors=backend_property.section.total_floors
        )

        property = await self.property_repo.update(property, data=property_data)
        return status, property

    async def _load_property_from_backend(self, backend_property_id: str) -> Optional[BackendProperty]:
        """
        Запрос получение объектов недвижимости из бэкенда
        """
        floors_qs = self.backend_floors_repo.list(
            filters=dict(section_id=F(table=Selectable(BackendSection.Meta.table), name="id")),
            end=1,
            start=0,
            ordering="-number"
        ).values("number")

        section_qs = self.backend_sections_repo.list(
            filters=dict(building_id=F(table=Selectable(BackendSection.Meta.table), name="id")),
            end=1,
            start=0,
            ordering="-max_number",
            annotations=dict(max_number=Subquery(floors_qs)),
        ).values("max_number")

        query = self.backend_properties_repo.retrieve(
            filters=dict(id=backend_property_id),
            related_fields=["building", "project", "floor", "section", "project__city"],
            prefetch_fields=["building__booking_types"],
            annotations=dict(total_floors=Subquery(section_qs)),
        )
        # Хак, чтобы sql нормально сгенерировался. Баг TortoiseORM или PyPika
        query._annotations["total_floors"].query.annotations["max_number"].alias = "max_number"
        return await query

    async def periodic(self) -> bool:
        """
        Переодический запуск
        """
        await self.orm_class.init(config=self.orm_config)
        await self.import_building_booking_types_service()
        async for property in self.property_repo.list():
            try:
                await self(property=property)
            except Exception:
                continue
        await self.orm_class.close_connections()
        return True

    async def _get_similar_property_from_backend(self, backend_property: BackendProperty) -> Optional[BackendProperty]:
        """
        Запрос на получение объекта недвижимости с похожей планировкой
        """
        similar_property = await self.backend_properties_repo.retrieve(
            filters=dict(
                id__not_in=[backend_property.id],
                layout_id=backend_property.layout_id,
                status=PropertyStatuses.FREE)
        )
        return similar_property

    async def _get_special_offers_from_backend(self, backend_property_id: str) -> list[Optional[str]]:
        """
        Запрос на получение акций объекта недвижимости
        """
        special_offers: BackendSpecialOfferProperty = await self.backend_special_offers_repo.list(
            filters=dict(
                property_id=backend_property_id,
                specialoffer__is_active=True
            ),
            related_fields=["specialoffer"]
        )
        special_offers_names = [special_offer.specialoffer.name for special_offer in special_offers]
        return ", ".join(special_offers_names)
