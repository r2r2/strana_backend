from typing import List, Optional
from decimal import Decimal
from pydantic import BaseModel, Field


class Template(BaseModel):
    area: Optional[int]
    price: Optional[int]
    client: Optional[str]
    akcia: Optional[tuple[str]]
    akciaDiscountEnabled: Optional[tuple[str]]
    angular: Optional[str]
    apartment: Optional[str]
    balcony: Optional[str]
    bathroom_window: Optional[str]
    bedroom_master1: Optional[str]
    bedroom_master2: Optional[str]
    bedroom_master3: Optional[str]
    bookedUntilDate: Optional[str]
    boulevard_windows: Optional[str]
    ceil_height: Optional[str]
    cityhouse: Optional[str]
    client: Optional[str]
    corner_loggia: Optional[str]
    corner_windows: Optional[str]
    creationDate: Optional[str]
    design_by_project: Optional[str]
    discountPrice: Optional[tuple[str]]
    floor: Optional[str]
    free_layout: Optional[str]
    french_balcony: Optional[str]
    front_garden: Optional[str]
    frontdoor: Optional[str]
    grocery: Optional[str]
    high_ceil: Optional[str]
    isEuro: Optional[str]
    isStudio: Optional[str]
    laundry: Optional[str]
    layout: Optional[str]
    loggia: Optional[str]
    manager: Optional[str]
    panoramic_glazing: Optional[str]
    panoramic_windows: Optional[str]
    parking: Optional[str]
    patio: Optional[str]
    penthouse: Optional[str]
    pochta: Optional[str]
    price: Optional[int]
    priceWithCash: Optional[str]
    price_with_furnishing: Optional[str]
    price_with_kitchen: Optional[str]
    price_with_renovation: Optional[str]
    prop_id: Optional[str]
    propertyStatusPBField: Optional[str]
    rieltor: Optional[str]
    roomsCount: Optional[int]
    separate_entrance_group: Optional[str]
    smart_house: Optional[str]
    telephone: Optional[str]
    terrace: Optional[str]
    three_side_window: Optional[str]
    two_bathrooms: Optional[str]
    two_side_window: Optional[str]
    view_on_bay: Optional[str]
    view_on_cathedral: Optional[str]
    view_on_park: Optional[str]
    view_on_river: Optional[str]
    view_on_square: Optional[str]
    wardrobe: Optional[str]
    wardrobe_window: Optional[str]
    warm_loggia: Optional[str]
    yard_window: Optional[str]
    zenith_window: Optional[str]
    house_id: Optional[str]
    entresol: Optional[str]


class Data(BaseModel):
    pageHeader: Optional[str]
    templates: Optional[List[Template]]


class Metadata(BaseModel):
    lead_id: int
    main_contact_id: int
    user_id: int


class TildaPostPayloadModel(BaseModel):
    data: Optional[Data]
    metadata: Optional[Metadata]
    page_id: Optional[int]
    site_id: Optional[int]
    url: Optional[str]


class TildaPostResponseDataModel(BaseModel):
    url: str
    generate_count: int


class TildaPostResponseModel(BaseModel):
    success: bool
    detail: str
    data: TildaPostResponseDataModel


class TildaAmoOfferPropertyBuildingModel(BaseModel):
    id: Optional[int]
    name: Optional[str]


class TildaAmoOfferPropertyModel(BaseModel):
    floor: Optional[int]
    house: Optional[TildaAmoOfferPropertyBuildingModel]
    id: Optional[int]
    name: Optional[str]
    sectionName: Optional[str]
    area: Optional[Decimal] = Field(max_digits=6, decimal_places=2)
    image: Optional[str]
    price: Optional[int]


class TildaAmoOfferModel(BaseModel):
    properties: Optional[list[TildaAmoOfferPropertyModel]]
    coLink: str
