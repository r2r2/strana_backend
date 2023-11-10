from typing import Callable, List, Optional, Any, Set
from datetime import date
from fastapi.encoders import jsonable_encoder
from tortoise.fields import ForeignKeyNullableRelation, ManyToManyRelation
from tortoise.queryset import ValuesListQuery, QuerySet
from src.properties.services import ImportPropertyService
from src.properties.repos import PropertyRepo, PropertyTypeRepo, Property, Feature
from src.projects.repos import ProjectRepo
from src.booking.repos import BookingRepo, Booking
from src.users.repos import UserRepo, User
from src.booking.types import BookingAmoCRM
from src.commercial_offers.models import RequestCreateOfferModel
from common.tilda.models.entities import (
    TildaPostPayloadModel,
    Template,
    Data,
    Metadata,
    TildaAmoOfferPropertyModel,
    TildaAmoOfferPropertyBuildingModel,
    TildaAmoOfferModel
)
from common.tilda.tilda import Tilda
from common.requests import CommonResponse
from src.buildings.repos.building import Building
from common.utils import from_global_id

from ..entities import BaseOfferCase
from ..repos.offer import OfferRepo, Offer
from ..repos.offer_source import OfferSource, OfferSourceRepo
from ..repos.offer_property import OfferPropertyRepo, OfferProperty
from ..repos.offer_template import OfferTemplateRepo, OfferTemplate
from ..exceptions import LeadNotFoundError, ClientNotFoundError
from ..constans import OfferConstants


class CreateOfferCaseSaving(BaseOfferCase):

    def __init__(
            self,
            import_property_service: ImportPropertyService,
            property_repo: type[PropertyRepo],
            property_type_repo: type[PropertyTypeRepo],
            booking_repo: type[BookingRepo],
            user_repo: type[UserRepo],
            amocrm_class: type[BookingAmoCRM],
            global_id_decoder: Callable,
            project_repo: type[ProjectRepo],
            offer_repo: type[OfferRepo],
            offer_source_repo: type[OfferSourceRepo],
            offer_properties_repo: type[OfferPropertyRepo],
            offer_template_repo: type[OfferTemplateRepo]
    ) -> None:
        self.property_repo: PropertyRepo = property_repo()
        self.property_type_repo: PropertyTypeRepo = property_type_repo()
        self.booking_repo: BookingRepo = booking_repo()
        self.user_repo: UserRepo = user_repo()
        self.import_property_service: ImportPropertyService = import_property_service
        self.amocrm_class: type[BookingAmoCRM] = amocrm_class
        self.global_id_decoder: Callable = global_id_decoder
        self.project_repo: ProjectRepo = project_repo()
        self.offer_repo: OfferRepo = offer_repo()
        self.offer_source_repo: OfferSourceRepo = offer_source_repo()
        self.offer_properties_repo: OfferPropertyRepo = offer_properties_repo()
        self.offer_template_repo: OfferTemplateRepo = offer_template_repo()

    async def __call__(self, payload: RequestCreateOfferModel, *args, **kwargs):

        # Получение сделки
        lead_filters: dict[str: int] = dict(amocrm_id=payload.meeting_amo_id)
        select_releated_fields: list[str] = ['agency', ]
        lead = await self.booking_repo.retrieve(filters=lead_filters, related_fields=select_releated_fields)
        if not lead:
            raise LeadNotFoundError()
        # Получение property
        properties: List[Property] = await self._get_properties(payload)
        # Анализ клиент
        client_filters: dict[str: int] = dict(amocrm_id=payload.client_amo_id)
        client: User = await self.user_repo.retrieve(filters=client_filters)
        if not client:
            raise ClientNotFoundError()
        # Подготовка payload для создания POST запроса
        tilda_payload: TildaPostPayloadModel = await self._get_tilda_post_payload(client, lead, properties, payload)
        # Отправка запроса на создание КП в Тильде, получение ссылки
        async with await Tilda() as tilda:
            tilda_post_response: CommonResponse = await tilda.save_kp(tilda_payload)
        try:
            tilda_response_data: dict = tilda_post_response.data
            offer_link: str = tilda_response_data.get("data").get("url")
        except AttributeError:
            tilda_response_data: dict = {}
            offer_link: str = ""

        if payload.is_save_lk:
            # Создание КП в БД
            offer_source_filters: dict[str: str] = dict(slug=OfferConstants.OFFER_SOURCE.value)
            offer_source: OfferSource = await self.offer_source_repo.retrieve(filters=offer_source_filters)
            offer_filters: dict = dict(
                booking_amo_id=payload.meeting_amo_id,
                client_amo_id=payload.client_amo_id
            )
            offer_data: dict = {
                "source": offer_source,
                "offer_link": offer_link
            }
            offer: Offer = await self.offer_repo.update_or_create(filters=offer_filters, data=offer_data)
            for property_ in properties:
                property_data: dict[str: Any] = {
                    "offer": offer,
                    "property_glogal_id": property_.global_id
                }
                offer_property: OfferProperty = await self.offer_properties_repo.create(data=property_data)

            # Подготовка структуры данных для отправки КП в АМО
            tilda_amo_offer = TildaAmoOfferModel()
            tilda_amo_offers: Optional[list[TildaAmoOfferPropertyModel]] = []
            for property_ in properties:
                template: TildaAmoOfferPropertyModel = TildaAmoOfferFields()(
                    offer_amo_property=TildaAmoOfferPropertyModel(),
                    property_=property_,
                    payload=payload
                )
                tilda_amo_offers.append(template)
            tilda_amo_offer.properties = tilda_amo_offers
            tilda_amo_offer_json = jsonable_encoder(tilda_amo_offer)

            # Отправка запроса на редактирование сделки в АМО, сохранение КП в специальное поле (try except)
            async with await self.amocrm_class() as amocrm:
                lead_options: dict[str, Any] = dict(
                    lead_id=lead.amocrm_id,
                    tilda_offer_amo=tilda_amo_offer_json,
                )
                await amocrm.update_lead_v4(**lead_options)

            return tilda_response_data

        # Отправка запроса на редактирование сделки в АМО, сохранение КП в комментарий
        note_message = f"Добавлено коммерческое предложение. Ссылка на КП: {offer_link}"
        async with await self.amocrm_class() as amocrm:
            await amocrm.create_note(lead_id=lead.amocrm_id, text=note_message, element="lead", note="common")

        return tilda_response_data

    async def _get_tilda_post_payload(self,
                                      client: User,
                                      lead: Booking,
                                      properties: List[Property],
                                      payload: RequestCreateOfferModel) -> TildaPostPayloadModel:
        tilda_payload: TildaPostPayloadModel = TildaPostPayloadModel()

        tilda_payload.metadata = Metadata(
            lead_id=lead.amocrm_id,
            main_contact_id=client.amocrm_id,
            user_id=0
        )

        buildings: Set[ForeignKeyNullableRelation[Building]] = set(
            [property_.building_id for property_ in properties])
        offer_template_filters: dict[str: int] = dict(building_id__in=buildings)
        offer_template: OfferTemplate = await self.offer_template_repo.retrieve(filters=offer_template_filters)
        if not offer_template:
            offer_template_filters: dict[str: int] = dict(is_default=True)
            offer_template: OfferTemplate = await self.offer_template_repo.retrieve(filters=offer_template_filters)
        tilda_payload.site_id = offer_template.site_id
        tilda_payload.page_id = offer_template.page_id
        tilda_payload.url = offer_template.link

        data = Data(
            pageHeader="",
            templates=[]
        )
        for property_ in properties:
            template: Template = TildaTemplateFields()(
                template=Template(),
                property_=property_,
                client=client,
                lead=lead,
                payload=payload
            )
            data.templates.append(template)
        tilda_payload.data = data
        return tilda_payload

    async def _get_properties(self, payload: RequestCreateOfferModel) -> List[Property]:
        properties: List[Property] = []
        for global_id in payload.property_global_ids:
            property_filters: dict[str: str] = dict(global_id=global_id)
            select_releated_fields: list[str] = ['floor', 'building', 'section']
            prefetch_releated_fields: list[str] = ['property_features']
            property_: Property = await self.property_repo.retrieve(
                filters=property_filters,
            )
            if not property_:
                data = dict(global_id=global_id)
                property_ = await self.property_repo.create(data)
            await self.import_property_service(property=property_)
            property_: Property = await self.property_repo.retrieve(
                filters=property_filters,
                related_fields=select_releated_fields,
                prefetch_fields=prefetch_releated_fields
            )

            properties.append(property_)
        return properties


class TildaTemplateFields:

    def __call__(self,
                 template: Template,
                 property_: Property,
                 client: User,
                 lead: Booking,
                 payload: RequestCreateOfferModel) -> Template:
        features: ManyToManyRelation["Feature"] = property_.property_features

        template.area = property_.area
        template.price = property_.price
        template.client = f"{client.name} {client.surname} {client.patronymic}"
        template.akcia = property_.special_offers if property_.special_offers else ""
        template.akciaDiscountEnabled = "Да" if property_.special_offers else ""
        template.angular = "Да" if property_.is_angular else ""
        template.apartment = property_.number
        template.balcony = "Да" if (property_.balconies_count and property_.balconies_count > 0) else ""
        template.bathroom_window = "Да" if property_.is_bathroom_window else ""
        template.bedroom_master1 = "Да" if self._is_related_feature(
            profitbase_id="pbcf_628e105253d7f",
            features=features) else ""
        template.bedroom_master2 = "Да" if property_.master_bedroom else ""
        template.bedroom_master3 = "Да" if self._is_related_feature(
            profitbase_id="pbcf_628e105cd2ec4",
            features=features) else ""
        template.bookedUntilDate = str(payload.booked_until_date) if payload.booked_until_date else ""
        template.boulevard_windows = "Да" if "Бульвар" in property_.window_view_profitbase else ""
        template.ceil_height = property_.ceil_height if property_.ceil_height else ""
        template.cityhouse = "Да" if property_.is_cityhouse else ""
        template.corner_loggia = "Да" if self._is_related_feature(
            profitbase_id="pbcf_628e102ab241b",
            features=features) else ""
        template.corner_windows = "Да" if property_.corner_windows else ""
        template.creationDate = str(date.today())
        template.design_by_project = "Да" if self._is_related_feature(
            profitbase_id="pbcf_63db466c2894c",
            features=features) else ""
        template.discountPrice = str(property_.final_price) if property_.final_price else ""
        template.floor = property_.floor.number
        template.free_layout = "Да" if property_.open_plan else ""
        template.french_balcony = "Да" if self._is_related_feature(
            profitbase_id="pbcf_5ec6621e549be",
            features=features) else ""
        template.front_garden = "Да" if property_.frontage else ""
        template.frontdoor = property_.section.name if property_.section.name else ""
        template.grocery = "Да" if self._is_related_feature(
            profitbase_id="pbcf_628e107ccef29",
            features=features) else ""
        template.high_ceil = "Да" if property_.has_high_ceiling else ""
        template.isEuro = "Да" if property_.is_euro_layout else ""
        template.isStudio = "Да" if property_.is_studio else ""
        template.laundry = "Да" if self._is_related_feature(
            profitbase_id="pbcf_61fce79fccd6d",
            features=features) else ""
        template.layout = property_.profitbase_plan
        template.loggia = "Да" if (property_.loggias_count and property_.loggias_count > 0) else ""
        template.manager = payload.manager_name
        template.panoramic_glazing = "Да" if self._is_related_feature(
            profitbase_id="pbcf_636b83172c3c7",
            features=features) else ""
        template.panoramic_windows = "Да" if property_.has_panoramic_windows else ""
        template.parking = "Да" if property_.has_parking else ""
        template.patio = "Да" if self._is_related_feature(
            profitbase_id="pbcf_636b83365f4a1",
            features=features) else ""
        template.penthouse = "Да" if property_.is_penthouse else ""
        template.pochta = payload.manager_login
        template.priceWithCash = str(property_.final_price) if property_.final_price else ""
        template.price_with_furnishing = property_.furnish_price_per_meter if property_.furnish_price_per_meter else ""
        template.price_with_kitchen = payload.price_with_kitchen if payload.price_with_kitchen else ""
        template.price_with_renovation = payload.price_with_renovation if payload.price_with_renovation else ""
        template.prop_id = from_global_id(property_.global_id)[1]
        template.propertyStatusPBField = "Забронировано" if lead.profitbase_booked else "Свободно"
        template.rieltor = lead.agency.name if lead.agency else ""
        template.roomsCount = property_.rooms
        template.separate_entrance_group = "Да" if self._is_related_feature(
            profitbase_id="pbcf_610151234ba57",
            features=features) else ""
        template.smart_house = "Да" if property_.smart_house else ""
        template.telephone = payload.manager_phone if payload.manager_phone else ""
        template.terrace = "Да" if property_.has_terrace else ""
        template.three_side_window = "Да" if self._is_related_feature(
            profitbase_id="pbcf_62d8f2a6a07d2",
            features=features) else ""
        template.two_bathrooms = "Да" if self._is_related_feature(
            profitbase_id="pbcf_5f2a867d95534",
            features=features) else ""
        template.two_side_window = "Да" if property_.has_two_sides_windows else ""
        template.view_on_bay = "Да" if self._is_related_feature(
            profitbase_id="pbcf_6188c33359e6e",
            features=features) else ""
        template.view_on_cathedral = "Да" if self._is_related_feature(
            profitbase_id="pbcf_6188c3455d663",
            features=features) else ""
        template.view_on_park = "Да" if property_.view_park else ""
        template.view_on_river = "Да" if property_.view_river else ""
        template.view_on_square = "Да" if property_.view_square else ""
        template.wardrobe = "Да" if (property_.wardrobes_count and property_.wardrobes_count > 0) else ""
        template.wardrobe_window = "Да" if self._is_related_feature(
            profitbase_id="pbcf_628e1086e4589",
            features=features) else ""
        template.warm_loggia = "Да" if self._is_related_feature(
            profitbase_id="pbcf_6006d5192faaa",
            features=features) else ""
        template.yard_window = "Да" if "Двор" in property_.window_view_profitbase else ""
        template.zenith_window = "Да" if self._is_related_feature(
            profitbase_id="pbcf_62a82476e2d13",
            features=features) else ""
        template.house_id = str(from_global_id(property_.building.global_id)[1])

        return template

    def _is_related_feature(self, profitbase_id: str, features: ManyToManyRelation["Feature"]) -> bool:
        result = False
        for feature in features:
            if feature.profit_id == profitbase_id:
                result = True
                break
        return result


class TildaAmoOfferFields:

    def __call__(self,
                 offer_amo_property: TildaAmoOfferPropertyModel,
                 property_: Property,
                 payload: RequestCreateOfferModel) -> TildaAmoOfferPropertyModel:
        offer_amo_property.floor = int(property_.floor.number)
        building = TildaAmoOfferPropertyBuildingModel(
            id=str(from_global_id(property_.building.global_id)[1]),
            name=property_.building.name
        )
        offer_amo_property.house = building
        offer_amo_property.id = int(from_global_id(property_.global_id)[1])
        offer_amo_property.name = property_.number
        offer_amo_property.sectionName = property_.section.number
        offer_amo_property.area = property_.area
        offer_amo_property.image = property_.profitbase_plan
        offer_amo_property.price = property_.price

        return offer_amo_property
