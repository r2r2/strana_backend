from typing import Optional
from ..entities import BaseOfferCamelCaseModel


class RequestCreateOfferModel(BaseOfferCamelCaseModel):
    """
    Модель запроса создания сделки
    """
    client_amo_id: int
    meeting_amo_id: int
    property_global_ids: list[str]
    manager_name: str
    manager_login: str
    is_save_lk: bool
    building_profitbase_id: Optional[int]
    layout_plan: Optional[str]
    booked_until_date: Optional[str]
    is_angular: Optional[bool]
    is_balcony: Optional[bool]
    is_bathroom_window: Optional[bool]
    is_master_bedroom1: Optional[bool]
    is_master_bedroom2: Optional[bool]
    is_master_bedroom3: Optional[bool]
    is_boulevard_windows: Optional[bool]
    ceil_height: Optional[str]
    is_cityhouse: Optional[bool]
    is_corner_loggia: Optional[bool]
    is_corner_windows: Optional[bool]
    is_design_by_project: Optional[bool]
    discount_price: Optional[str]
    is_open_plan: Optional[bool]
    is_french_balcony: Optional[bool]
    is_frontage: Optional[bool]
    section_name: Optional[str]
    is_grocery: Optional[bool]
    is_high_ceil: Optional[bool]
    is_euro_layout: Optional[bool]
    is_studio: Optional[bool]
    is_laundry: Optional[bool]
    is_loggia: Optional[bool]
    is_panoramic_glazing: Optional[bool]
    is_panoramic_windows: Optional[bool]
    is_parking: Optional[bool]
    is_patio: Optional[bool]
    is_penthouse: Optional[bool]
    furnish_price_per_meter: Optional[str]
    price_with_kitchen: Optional[str]
    price_with_renovation: Optional[str]
    rieltor: Optional[str]
    is_separate_entrance_group: Optional[str]
    is_smart_house: Optional[bool]
    manager_phone: Optional[str]
    is_terrace: Optional[bool]
    is_three_side_window: Optional[bool]
    is_two_bathrooms: Optional[bool]
    is_two_side_window: Optional[bool]
    is_view_on_bay: Optional[bool]
    is_view_on_cathedral: Optional[bool]
    is_view_park: Optional[bool]
    is_view_river: Optional[bool]
    is_view_square: Optional[bool]
    is_wardrobe: Optional[bool]
    is_wardrobe_window: Optional[bool]
    is_warm_loggia: Optional[bool]
    is_yard_window: Optional[bool]
    is_zenith_window: Optional[bool]


