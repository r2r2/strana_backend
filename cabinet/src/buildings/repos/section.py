from typing import Optional

from tortoise import Model, fields

from common import orm
from common.orm.mixins import ReadWriteMixin
from ..entities import BaseBuildingRepo


class BuildingSection(Model):
    """
    Секция
    """
    id: int = fields.IntField(pk=True)
    name: Optional[str] = fields.CharField(description="Название", max_length=50, null=True)
    total_floors: Optional[int] = fields.IntField(null=True)
    number = fields.CharField(description="Название", max_length=50, default="-")

    building: fields.ForeignKeyRelation["Building"] = fields.ForeignKeyField(
        "models.Building", null=True, on_delete=fields.CASCADE, related_name="building_section"
    )
    building_id: int

    class Meta:
        table = "buildings_section"


class BuildingSectionRepo(BaseBuildingRepo, ReadWriteMixin):
    """
    Репозиторий корпуса
    """
    model = BuildingSection
    a_builder: orm.AnnotationBuilder = orm.AnnotationBuilder(BuildingSection)
