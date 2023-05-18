from typing import Optional

from tortoise import Model, fields


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

    class Meta:
        app = "backend"
        table = "buildings_building"
