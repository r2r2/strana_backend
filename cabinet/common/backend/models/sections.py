from typing import Optional

from tortoise import Model, fields

from .buildings import BackendBuilding


class BackendSection(Model):
    id: int = fields.IntField(pk=True)
    name: Optional[str] = fields.CharField(description="Название", max_length=50, null=True)
    total_floors: Optional[int] = fields.IntField(null=True)
    number = fields.CharField(description="Название", max_length=50, default="-")

    building: fields.ForeignKeyRelation[BackendBuilding] = fields.ForeignKeyField(
        "backend.BackendBuilding", null=True, on_delete=fields.CASCADE, related_name="building_section"
    )
    building_id: int

    class Meta:
        app = "backend"
        table = "buildings_section"
