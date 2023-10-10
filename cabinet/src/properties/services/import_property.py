# pylint: disable=protected-access,broad-except,redefined-builtin
from copy import copy
from typing import Callable

from pypika.queries import Selectable
from tortoise.expressions import F, Subquery

from common import utils
from common.backend import repos as backend_repos
from common.backend.models import (
    BackendBuilding,
    BackendBuildingBookingType,
    BackendCity,
    BackendFloor,
    BackendMetro,
    BackendMetroLine,
    BackendProject,
    BackendProperty,
    BackendSection,
    BackendSpecialOfferProperty,
    BackendTransport,
)
from common.backend.repos import (
    BackendBuildingBookingTypesRepo,
    BackendFloorsRepo,
    BackendPropertiesRepo,
    BackendSectionsRepo,
    BackendSpecialOfferRepo,
)
from src.buildings.repos import (
    BuildingBookingType,
    BuildingBookingTypeRepo,
    BuildingRepo,
    BuildingSection,
    BuildingSectionRepo,
    Building,
)
from src.cities.repos import (
    City,
    CityRepo,
    Metro,
    MetroLine,
    MetroLineRepo,
    MetroRepo,
    Transport,
    TransportRepo,
)
from src.floors.repos import FloorRepo
from src.projects.repos import ProjectRepo
from src.properties.constants import PropertyStatuses
from src.properties.repos import Feature, FeatureRepo, PropertyRepo

from .import_building_booking_types import ImportBuildingBookingTypesService
from ..entities import BasePropertyService
from ..repos import Property, PropertyTypeRepo
from ..types import (
    PropertyBuildingRepo,
    PropertyFloorRepo,
    PropertyORM,
    PropertyProjectRepo,
)


class ImportPropertyService(BasePropertyService):
    """
    Импорт объекта недвижимости с бэкенда
    """

    property_types_mapping: dict = {
        "flat": "GlobalFlatType",
        "pantry": "GlobalPantryType",
        "parking": "GlobalParkingSpaceType",
        "commercial": "GlobalCommercialSpaceType",
        "commercial_apartment": "GlobalFlatType",
    }
    related_types_mapping: dict = {
        "city": ("CityType", "id"),
        "floor": ("FloorType", "id"),
        "building": ("BuildingType", "id"),
        "project": ("GlobalProjectType", "slug"),
    }

    def __init__(
        self,
        property_repo: type[PropertyRepo],
        floor_repo: type[PropertyFloorRepo],
        project_repo: type[PropertyProjectRepo],
        building_repo: type[PropertyBuildingRepo],
        building_booking_type_repo: type[BuildingBookingTypeRepo],
        backend_building_booking_type_repo: type[BackendBuildingBookingTypesRepo],
        backend_properties_repo: type[BackendPropertiesRepo],
        backend_floors_repo: type[BackendFloorsRepo],
        backend_sections_repo: type[BackendSectionsRepo],
        feature_repo: type[FeatureRepo],
        global_id_encoder: Callable[[str, str], str],
        global_id_decoder: Callable[[str], list[str]],
        orm_class: type[PropertyORM] | None = None,
        orm_config: dict | None = None,
        import_building_booking_types_service: ImportBuildingBookingTypesService | None = None,
        backend_special_offers_repo: type[BackendSpecialOfferRepo] | None = None,
        property_type_repo: type[PropertyTypeRepo] | None = None,
        city_repo: type[CityRepo] = CityRepo,
    ) -> None:
        self.floor_repo: PropertyFloorRepo = floor_repo()
        self.property_repo: PropertyRepo = property_repo()
        self.project_repo: PropertyProjectRepo = project_repo()
        self.city_repo: CityRepo = city_repo()
        self.building_repo: PropertyBuildingRepo = building_repo()
        self.features_repo: FeatureRepo = feature_repo()
        self.metro_repo: MetroRepo = MetroRepo()
        self.metro_line_repo: MetroLineRepo = MetroLineRepo()
        self.transport_repo: TransportRepo = TransportRepo()
        self.transport_repo: TransportRepo = TransportRepo()
        self.section_repo: BuildingSectionRepo = BuildingSectionRepo()

        self.building_booking_type_repo: BuildingBookingTypeRepo = (
            building_booking_type_repo()
        )
        self.backend_building_booking_type_repo: BackendBuildingBookingTypesRepo = (
            backend_building_booking_type_repo()
        )
        self.backend_properties_repo: BackendPropertiesRepo = backend_properties_repo()
        self.backend_building_section_repo: BackendSectionsRepo = BackendSectionsRepo()
        self.backend_floors_repo: BackendFloorsRepo = backend_floors_repo()
        self.backend_sections_repo: BackendSectionsRepo = backend_sections_repo()
        self.import_building_booking_types_service = (
            import_building_booking_types_service
        )
        if backend_special_offers_repo:
            self.backend_special_offers_repo: BackendSpecialOfferRepo = (
                backend_special_offers_repo()
            )
        else:
            self.backend_special_offers_repo = None

        # if property_type_repo:
        #     self.property_type_repo: PropertyTypeRepo = property_type_repo()
        # else:
        #     self.property_type_repo = None
        self.property_type_repo: PropertyTypeRepo = PropertyTypeRepo()

        self.global_id_encoder: Callable[[str, str], str] = global_id_encoder
        self.global_id_decoder: Callable[[str], list[str]] = global_id_decoder

        self.orm_class: type[PropertyORM] | None = orm_class
        self.orm_config: dict | None = copy(orm_config)
        if self.orm_config:
            self.orm_config.pop("generate_schemas", None)

    async def update_features(
        self, backend_property: BackendProperty, _property: Property
    ) -> Property:
        features_for_city = await backend_property.project.city.features
        featuries_for_update = [
            feature
            for feature in features_for_city
            if f"'{backend_property.type}'" in feature.property_kind.value
        ]
        if featuries_for_update:
            for back_feature in featuries_for_update:
                feature: Feature = await self.features_repo.update_or_create(
                    filters=dict(
                        backend_id=back_feature.id,
                    ),
                    data=dict(
                        name=back_feature.name,
                        filter_show=back_feature.filter_show,
                        main_filter_show=back_feature.main_filter_show,
                        lot_page_show=back_feature.lot_page_show,
                        icon_show=back_feature.icon_show,
                        icon=back_feature.icon,
                        icon_flats_show=back_feature.icon_flats_show,
                        icon_hypo=back_feature.icon_hypo,
                        icon_flats=back_feature.icon_flats,
                        description=back_feature.description,
                        order=back_feature.order,
                        is_button=back_feature.is_button,
                    ),
                )
                await _property.property_features.add(feature)

        return _property

    async def __call__(
        self, property_id: int | None = None, property: Property | None = None
    ) -> tuple[bool, Property]:
        _property = property
        if not _property:
            filters: dict = dict(id=property_id)
            _property: Property = await self.property_repo.retrieve(filters=filters)
        status: bool = True

        if not _property.global_id:
            return status, _property

        backend_property_id = self.global_id_decoder(_property.global_id)[1]
        backend_property = await self._load_property_from_backend(backend_property_id)
        if backend_property is None:
            return False, _property
        backend_project: BackendProject = backend_property.project
        await backend_project.fetch_related("metro__line", "transport")
        backend_city: BackendCity = backend_project.city
        backend_metro: BackendMetro = backend_project.metro
        backend_metro_line: BackendMetroLine = (
            backend_metro.line if backend_metro else None
        )
        backend_transport: BackendTransport = backend_project.transport
        backend_floor: BackendFloor = backend_property.floor
        backend_building: BackendBuilding = backend_property.building
        backend_building_booking_types: list[BackendBuildingBookingType] = list(
            backend_property.building.booking_types
        )
        backend_building_section: BackendSection = (
            await self.backend_building_section_repo.retrieve(
                filters=dict(building_id=backend_building.id)
            )
        )

        city: City = await self.city_repo.retrieve(filters=dict(slug=backend_city.slug))
        metro = None
        if backend_metro_line:
            metro_line: MetroLine = await self.metro_line_repo.update_or_create(
                filters=dict(city__slug=city.slug, name=backend_metro_line.name),
                data=dict(
                    color=backend_metro_line.color,
                    city_id=city.id,
                ),
            )

            metro: Metro | None = None
            if backend_metro and metro_line:
                metro: Metro = await self.metro_repo.update_or_create(
                    filters=dict(
                        name=backend_metro.name,
                        line__name=backend_metro_line.name,
                        line__city__id=city.id,
                    ),
                    data=dict(
                        latitude=backend_metro.latitude,
                        longitude=backend_metro.longitude,
                        line_id=metro_line.id,
                    ),
                )

        transport: Transport | None = None
        if backend_transport:
            transport: Transport = await self.transport_repo.update_or_create(
                filters=dict(name=backend_transport.name),
                data=dict(
                    icon=backend_transport.icon,
                    icon_content=backend_transport.icon_content,
                ),
            )

        project_global_id_type = self.related_types_mapping["project"][0]
        project_global_id_value = getattr(
            backend_project, self.related_types_mapping["project"][1], None
        )
        project_global_id = self.global_id_encoder(
            project_global_id_type, project_global_id_value
        )

        project_data = dict(
            name=backend_project.name,
            slug=backend_project.slug,
            amocrm_name=backend_project.amocrm_name,
            amocrm_enum=backend_project.amocrm_enum,
            amocrm_organization=backend_project.amocrm_organization,
            amo_pipeline_id=backend_project.amo_pipeline_id,
            amo_responsible_user_id=backend_project.amo_responsible_user_id,
            city_id=city.id,
            metro_id=metro.id if metro else None,
            transport_id=transport.id if transport else None,
            is_active=backend_project.active,
            status=backend_project.status,
            address=backend_project.address,
            transport_time=backend_project.transport_time,
            project_color=backend_project.project_color,
            title=backend_project.title,
            card_image=backend_project.card_image,
            card_image_night=backend_project.card_image_night,
            card_sky_color=backend_project.card_sky_color.value,
            min_flat_price=float(backend_project.min_flat_price)
            if backend_project.min_flat_price
            else None,
            min_flat_area=float(backend_project.min_flat_area)
            if backend_project.min_flat_area
            else None,
            max_flat_area=float(backend_project.max_flat_area)
            if backend_project.max_flat_area
            else None,
        )
        # Создаём/обновляем проект
        project = await self.project_repo.update_or_create(
            filters=dict(global_id=project_global_id), data=project_data
        )

        building_global_id_type = self.related_types_mapping["building"][0]
        building_global_id_value = getattr(
            backend_building, self.related_types_mapping["building"][1], None
        )

        building_global_id = self.global_id_encoder(
            building_global_id_type, building_global_id_value
        )
        building_data = dict(
            name=backend_building.name,
            name_display=backend_building.name_display,
            address=backend_building.address,
            ready_quarter=backend_building.ready_quarter,
            built_year=backend_building.built_year,
            booking_active=backend_building.booking_active,
            booking_period=backend_building.booking_period,
            booking_price=backend_building.booking_price,
            total_floor=backend_property.section.total_floors,
            project=project,
            kind=backend_building.kind.value,
            flats_0_min_price=backend_building.flats_0_min_price,
            flats_1_min_price=backend_building.flats_1_min_price,
            flats_2_min_price=backend_building.flats_2_min_price,
            flats_3_min_price=backend_building.flats_3_min_price,
            flats_4_min_price=backend_building.flats_4_min_price,
        )

        # Создаём/обновляем корпус
        building: Building = await self.building_repo.update_or_create(
            filters=dict(global_id=building_global_id), data=building_data
        )

        building_section: BuildingSection = await self.section_repo.update_or_create(
            filters=dict(building_id=building.id, property_section__id=_property.id),
            data=dict(
                name=backend_building_section.name,
                total_floors=backend_building_section.total_floors,
                number=backend_building_section.number,
            ),
        )
        # Создаём/обновляем типы бронирования у корпуса,
        # а также удаляем отвязанные от корпуса типы бронирования
        building_booking_types = await building.booking_types
        used_building_booking_type_ids: list[int] = (
            await self.backend_building_booking_type_repo.list()
            .distinct()
            .values_list("id", flat=True)
        )
        filters = dict(id__in=used_building_booking_type_ids)
        created_or_updated_booking_types: list[
            BuildingBookingType
        ] = await self.building_booking_type_repo.list(filters=filters)
        if created_or_updated_booking_types:
            await building.booking_types.add(*created_or_updated_booking_types)

        booking_types_for_unlinking: list[BuildingBookingType] = []
        for booking_type in building_booking_types:
            if booking_type.pk not in used_building_booking_type_ids:
                booking_types_for_unlinking.append(booking_type)
        if booking_types_for_unlinking:
            await building.booking_types.remove(*booking_types_for_unlinking)

        backend_building_periods: list[int] = [
            booking_type.period for booking_type in backend_building_booking_types
        ]
        building_booking_types: list[
            BuildingBookingType
        ] = await self.building_booking_type_repo.list(
            filters=dict(period__in=backend_building_periods)
        )
        if building_booking_types:
            # todo нужно будет специальный метод для m2m в миксины
            await building.booking_types.clear()  # удаляем ранее связанные типы
            await building.booking_types.add(*building_booking_types)  # повторная синхронизация типов с порталом

        # Создаём/обновляем этаж
        floor_global_id_type = self.related_types_mapping["floor"][0]
        floor_global_id_value = getattr(
            backend_floor, self.related_types_mapping["floor"][1], None
        )
        floor_global_id = self.global_id_encoder(
            floor_global_id_type, floor_global_id_value
        )
        floor_data = dict(
            number=backend_floor.number, building=building, section=building_section
        )
        floor = await self.floor_repo.update_or_create(
            filters=dict(global_id=floor_global_id), data=floor_data
        )

        # Привязываем модель типа объекта недвижимости из базы ЛК к объекту
        if not self.property_type_repo:
            property_type = None
        else:
            property_type = await self.property_type_repo.retrieve(
                filters=dict(slug=backend_property.type)
            )
            if not property_type:
                # Импортируем новый тип недвижимости (только слаг, название ставим временное,
                # помечаем как неактивный для дальнейшего заполнения в админке)
                property_type_data: dict = dict(
                    slug=backend_property.type,
                    label=backend_property.type,
                    is_active=False,
                )
                property_type = await self.property_type_repo.create(
                    data=property_type_data
                )

        # Создаём/обновляем квартиру
        property_global_id_type = self.property_types_mapping.get(backend_property.type)
        property_global_id_value = str(backend_property.id)
        property_global_id = self.global_id_encoder(
            property_global_id_type, property_global_id_value
        )

        # Получаем данные по похожему объекту недвижимости
        if self.backend_special_offers_repo:
            similar_property = await self._get_similar_property_from_backend(
                backend_property
            )
            if similar_property:
                similar_property_global_id_type = self.property_types_mapping.get(
                    similar_property.type
                )
                similar_property_global_id_value = str(similar_property.id)
                similar_property_global_id = self.global_id_encoder(
                    similar_property_global_id_type, similar_property_global_id_value
                )
            else:
                similar_property_global_id = None
            # Получаем данные по акциям для объекта недвижимости
            special_offers = await self._get_special_offers_from_backend(
                backend_property.id
            )
        else:
            similar_property_global_id = None
            special_offers = None
        property_data = dict(
            # global_id=property_global_id,
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
            total_floors=backend_property.section.total_floors,
            section_id=building_section.id,
            property_type_id=property_type.id if property_type else None,
        )
        _property = await self.property_repo.update(_property, data=property_data)
        _property = await self.update_features(backend_property, _property)

        return status, _property

    async def _load_property_from_backend(
        self, backend_property_id: str
    ) -> BackendProperty | None:
        """
        Запрос получение объектов недвижимости из бэкенда
        """
        floors_qs = self.backend_floors_repo.list(
            filters=dict(
                section_id=F(table=Selectable(BackendSection.Meta.table), name="id")
            ),
            end=1,
            start=0,
            ordering="-number",
        ).values("number")

        section_qs = self.backend_sections_repo.list(
            filters=dict(
                building_id=F(table=Selectable(BackendSection.Meta.table), name="id")
            ),
            end=1,
            start=0,
            ordering="-max_number",
            annotations=dict(max_number=Subquery(floors_qs)),
        ).values("max_number")

        query = self.backend_properties_repo.retrieve(
            filters=dict(id=backend_property_id),
            related_fields=[
                "building",
                "floor",
                "section",
                "project__city__metro_line",
                # "project__metro__line",
                # "project__transport",
            ],
            prefetch_fields=[
                "building__booking_types",
                "project__city__features",
            ],
            annotations=dict(
                total_floors=Subquery(section_qs),
            ),
        )
        # Хак, чтобы sql нормально сгенерировался. Баг TortoiseORM или PyPika
        query._annotations["total_floors"].query.annotations[
            "max_number"
        ].alias = "max_number"
        return await query

    async def periodic(self) -> bool:
        """
        Периодический запуск
        """
        await self.orm_class.init(config=self.orm_config)
        await self.import_building_booking_types_service()
        async for _property in self.property_repo.list():
            try:
                await self(property=_property)
            except Exception:
                continue
        await self.orm_class.close_connections()
        return True

    async def _get_similar_property_from_backend(
        self, backend_property: BackendProperty
    ) -> BackendProperty | None:
        """
        Запрос на получение объекта недвижимости с похожей планировкой
        """
        similar_property = await self.backend_properties_repo.retrieve(
            filters=dict(
                id__not_in=[backend_property.id],
                layout_id=backend_property.layout_id,
                status=PropertyStatuses.FREE,
            )
        )
        return similar_property

    async def _get_special_offers_from_backend(
        self, backend_property_id: str
    ) -> list[str | None]:
        """
        Запрос на получение акций объекта недвижимости
        """
        special_offers: BackendSpecialOfferProperty = (
            await self.backend_special_offers_repo.list(
                filters=dict(
                    property_id=backend_property_id, specialoffer__is_active=True
                ),
                related_fields=["specialoffer"],
            )
        )
        special_offers_names = [
            special_offer.specialoffer.name for special_offer in special_offers
        ]
        return ", ".join(special_offers_names)


class ImportPropertyServiceFactory:
    @staticmethod
    def create(
        orm_class=None, orm_config=None, import_building_booking_types_service=None
    ) -> ImportPropertyService:
        """
        Создание экземпляра сервиса импорта
        """
        import_property_service = ImportPropertyService(
            property_repo=PropertyRepo,
            floor_repo=FloorRepo,
            project_repo=ProjectRepo,
            building_repo=BuildingRepo,
            building_booking_type_repo=BuildingBookingTypeRepo,
            backend_building_booking_type_repo=backend_repos.BackendBuildingBookingTypesRepo,
            backend_properties_repo=backend_repos.BackendPropertiesRepo,
            backend_floors_repo=backend_repos.BackendFloorsRepo,
            backend_sections_repo=backend_repos.BackendSectionsRepo,
            feature_repo=FeatureRepo,
            global_id_decoder=utils.from_global_id,
            global_id_encoder=utils.to_global_id,
            orm_class=orm_class,
            orm_config=orm_config,
            import_building_booking_types_service=import_building_booking_types_service,
            backend_special_offers_repo=backend_repos.BackendSpecialOfferRepo,
            city_repo=CityRepo,
        )

        return import_property_service
