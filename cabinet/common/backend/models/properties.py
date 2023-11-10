from decimal import Decimal
from typing import Optional

from tortoise import Model, fields

from .buildings import BackendBuilding
from .floor import BackendFloor
from .projects import BackendProject
from .sections import BackendSection


class BackendProperty(Model):
    id: int = fields.IntField(pk=True)
    type: str = fields.CharField(max_length=20)
    article: str = fields.CharField(max_length=100)
    plan: str = fields.TextField()
    plan_png: str = fields.CharField(max_length=100)
    price: Decimal = fields.DecimalField(14, 2)
    original_price: Decimal = fields.DecimalField(14, 2)
    full_final_price: Decimal = fields.DecimalField(14, 2)
    area: Decimal = fields.DecimalField(8, 2)
    action: str = fields.CharField(max_length=50)
    status: int = fields.SmallIntField()
    rooms: int = fields.SmallIntField()
    number: str = fields.CharField(max_length=100)
    maternal_capital: bool = fields.BooleanField()
    preferential_mortgage: bool = fields.BooleanField()
    profitbase_plan: str = fields.CharField(max_length=512)

    building: fields.ForeignKeyRelation[BackendBuilding] = fields.ForeignKeyField(
        "backend.BackendBuilding", null=True, on_delete=fields.CASCADE
    )
    building_id: int
    project: fields.ForeignKeyRelation[BackendProject] = fields.ForeignKeyField(
        "backend.BackendProject", on_delete=fields.CASCADE
    )
    project_id: int
    floor: fields.ForeignKeyRelation[BackendFloor] = fields.ForeignKeyField(
        "backend.BackendFloor", null=True, on_delete=fields.CASCADE
    )
    floor_id: int
    section: fields.ForeignKeyNullableRelation[BackendSection] = fields.ForeignKeyField(
        "backend.BackendSection", null=True, on_delete=fields.CASCADE
    )
    section_id: int
    layout_id: Optional[int] = fields.IntField(null=True)

    is_angular: bool = fields.BooleanField(default=False)
    balconies_count: Optional[int] = fields.IntField(null=True)
    is_bathroom_window: bool = fields.BooleanField(default=False)
    master_bedroom: bool = fields.BooleanField(default=False)
    window_view_profitbase: Optional[str] = fields.CharField(max_length=100, null=True)
    ceil_height: Optional[str] = fields.CharField(max_length=16, null=True)
    is_cityhouse: bool = fields.BooleanField(default=False)
    corner_windows: bool = fields.BooleanField(default=False)
    open_plan: bool = fields.BooleanField(default=False)
    frontage: bool = fields.BooleanField(default=False)
    has_high_ceiling: bool = fields.BooleanField(default=False)
    is_euro_layout: bool = fields.BooleanField(default=False)
    is_studio: bool = fields.BooleanField(default=False)
    loggias_count: Optional[int] = fields.IntField(null=True)
    has_panoramic_windows: bool = fields.BooleanField(default=False)
    has_parking: bool = fields.BooleanField(default=False)
    is_penthouse: bool = fields.BooleanField(default=False)
    furnish_price_per_meter: Optional[Decimal] = fields.DecimalField(max_digits=14, decimal_places=2, null=True)
    is_discount_enable: bool = fields.BooleanField(default=False)
    profitbase_property_status: Optional[str] = fields.CharField(max_length=64, null=True)
    smart_house: bool = fields.BooleanField(default=False)
    has_terrace: bool = fields.BooleanField(default=False)
    has_two_sides_windows: bool = fields.BooleanField(default=False)
    view_park: bool = fields.BooleanField(default=False)
    view_river: bool = fields.BooleanField(default=False)
    view_square: bool = fields.BooleanField(default=False)
    wardrobes_count: Optional[int] = fields.IntField(null=True)
    profitbase_booked_until_date: Optional[str] = fields.CharField(max_length=64, null=True)


    class Meta:
        app = "backend"
        table = "properties_property"
