from decimal import Decimal

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
    area: Decimal = fields.DecimalField(8, 2)
    action: str = fields.CharField(max_length=50)
    status: int = fields.SmallIntField()
    rooms: int = fields.SmallIntField()
    number: str = fields.CharField(max_length=100)
    maternal_capital: bool = fields.BooleanField()
    preferential_mortgage: bool = fields.BooleanField()

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
    layout_id: int = fields.IntField()

    class Meta:
        app = "backend"
        table = "properties_property"
