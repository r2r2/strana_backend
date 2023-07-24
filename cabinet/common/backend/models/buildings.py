from typing import Optional

from tortoise import Model, fields

from common import cfields
from ..constaints import BuildingType


class BackendBuildingBookingType(Model):
    id: int = fields.IntField(pk=True)
    period: int = fields.SmallIntField(verbose_name="Длительность бронирования")
    price: int = fields.IntField(verbose_name="Стоимость бронирования")
    amocrm_id: int = fields.BigIntField(null=True, verbose_name='Идентификатор АМОЦРМ')

    class Meta:
        app = "backend"
        table = "buildings_buildingbookingtype"


class BackendBuilding(Model):
    id: int = fields.IntField(pk=True)
    name: Optional[str] = fields.CharField(max_length=200, null=True)
    name_display = fields.CharField(description="Отображаемое имя", max_length=100, null=True)
    address: Optional[str] = fields.CharField(max_length=300, null=True)
    ready_quarter: Optional[int] = fields.IntField(null=True)
    built_year: Optional[int] = fields.IntField(null=True)
    booking_active: bool = fields.BooleanField()
    booking_period: int = fields.SmallIntField()
    booking_price: int = fields.IntField()
    booking_types: list[BackendBuildingBookingType] = fields.ManyToManyField(
        "backend.BackendBuildingBookingType",
        through="buildings_building_booking_types",
        forward_key="buildingbookingtype_id",
        backward_key="building_id",
    )
    kind: str = cfields.CharChoiceField(
        description="Тип строения",
        default=BuildingType.RESIDENTIAL,
        choice_class=BuildingType,
        max_length=32,
    )
    flats_0_min_price = fields.DecimalField(description="Мин цена студия", max_digits=14, decimal_places=2, null=True)
    flats_1_min_price = fields.DecimalField(description="Мин цена 1-комн", max_digits=14, decimal_places=2, null=True)
    flats_2_min_price = fields.DecimalField(description="Мин цена 2-комн", max_digits=14, decimal_places=2, null=True)
    flats_3_min_price = fields.DecimalField(description="Мин цена 3-комн", max_digits=14, decimal_places=2, null=True)
    flats_4_min_price = fields.DecimalField(description="Мин цена 4-комн", max_digits=14, decimal_places=2, null=True)

    class Meta:
        app = "backend"
        table = "buildings_building"
