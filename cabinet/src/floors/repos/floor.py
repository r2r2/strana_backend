from typing import Optional

from tortoise import Model, fields
from tortoise.fields import ForeignKeyNullableRelation

from common import orm
from src.buildings.repos import Building
from common.orm.mixins import CreateMixin, UpdateOrCreateMixin, ListMixin
from ..entities import BaseFloorRepo


class Floor(Model):
    """
    Этаж
    """
    id: int = fields.IntField(description="ID", pk=True)
    global_id: Optional[str] = fields.CharField(
        description="Глобальный ID", max_length=200, unique=True, null=True
    )
    number: Optional[str] = fields.CharField(description="Номер", max_length=20, null=True)
    building: ForeignKeyNullableRelation[Building] = fields.ForeignKeyField(
        description="Корпус", model_name="models.Building", related_name="floors", null=True
    )
    section: fields.ForeignKeyNullableRelation["BuildingSection"] = fields.ForeignKeyField(
        "models.BuildingSection", null=True, on_delete=fields.CASCADE, related_name="section_floors"
    )

    def __str__(self) -> str:
        if self.number:
            return self.number
        return str(self.id)

    class Meta:
        table = "floors_floor"


class FloorRepo(BaseFloorRepo, CreateMixin, UpdateOrCreateMixin, ListMixin):
    """
    Репозиторий этажа
    """
    model = Floor
    a_builder: orm.AnnotationBuilder = orm.AnnotationBuilder(Floor)
