from typing import Optional

from tortoise import Model, fields

from .buildings import BackendBuilding


class BackendSection(Model):
    id: int = fields.IntField(pk=True)
    total_floors: Optional[int] = fields.IntField(null=True)

    building: fields.ForeignKeyRelation[BackendBuilding] = fields.ForeignKeyField(
        "backend.BackendBuilding", null=True, on_delete=fields.CASCADE
    )
    building_id: int

    class Meta:
        app = "backend"
        table = "buildings_section"
