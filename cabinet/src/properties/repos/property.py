from decimal import Decimal
from typing import Optional, Annotated

from pydantic import Field
from tortoise import Model, fields
from tortoise.fields import ForeignKeyNullableRelation

from common import cfields
from common.orm.mixins import CRUDMixin

from src.floors.repos import Floor
from src.projects.repos import Project
from src.buildings.repos import Building

from ..entities import BasePropertyRepo
from ..constants import PropertyStatuses, PropertyTypes, PremiseType


class Property(Model):
    """
    Объект недвижимости
    """

    types = PropertyTypes()
    premises = PremiseType()
    statuses = PropertyStatuses()

    id: int = fields.IntField(description="ID", pk=True)
    global_id: Optional[str] = fields.CharField(
        description="Глобальный ID", max_length=200, unique=True, null=True
    )
    type: Optional[str] = cfields.CharChoiceField(
        description="Тип", max_length=50, null=True, choice_class=PropertyTypes
    )
    article: Optional[str] = fields.CharField(description="Артикул", max_length=50, null=True)
    plan: Annotated[str, Field(max_length=300)] = cfields.MediaField(
        description="Планировка", max_length=300, null=True
    )
    plan_png: Annotated[str, Field(max_length=300)] = cfields.MediaField(
        description="Планировка png", max_length=300, null=True
    )
    price: Optional[int] = fields.BigIntField(description="Цена", null=True)
    original_price: Optional[int] = fields.BigIntField(description="Оригинальная цена", null=True)
    final_price: Optional[int] = fields.BigIntField(description="Конечная цена", null=True)
    area: Optional[Decimal] = fields.DecimalField(
        description="Площадь", decimal_places=2, max_digits=7, null=True
    )
    deadline: Optional[str] = fields.CharField(description="Срок сдачи", max_length=50, null=True)
    discount: Optional[int] = fields.BigIntField(description="Скидка", null=True)
    status: Optional[int] = cfields.SmallIntChoiceField(
        description="Статус", null=True, choice_class=PropertyStatuses
    )
    rooms: Optional[int] = fields.SmallIntField(description="Комнат", null=True)
    number: Optional[str] = fields.CharField(description="Номер", max_length=100, null=True)
    premise: Optional[str] = cfields.CharChoiceField(
        description="Помещение",
        max_length=30,
        null=True,
        choice_class=PremiseType,
        default=PremiseType.RESIDENTIAL,
    )
    total_floors: Optional[int] = fields.SmallIntField(description="Всего этажей", null=True)
    project: ForeignKeyNullableRelation[Project] = fields.ForeignKeyField(
        description="Проект", model_name="models.Project", related_name="properties", null=True
    )
    building: ForeignKeyNullableRelation[Building] = fields.ForeignKeyField(
        description="Корпус", model_name="models.Building", related_name="properties", null=True
    )
    floor: ForeignKeyNullableRelation[Floor] = fields.ForeignKeyField(
        description="Этаж", model_name="models.Floor", related_name="properties", null=True
    )
    special_offers: Optional[str] = fields.TextField(description="Акции", null=True)
    similar_property_global_id: Optional[str] = fields.CharField(
        description="Id Квартиры с похожей планировкой",
        max_length=200,
        null=True
    )

    maternal_capital: bool = fields.BooleanField(description="Материнский капитал", default=False)
    preferential_mortgage: bool = fields.BooleanField(description="Льготная ипотека", default=False)

    bookings: ForeignKeyNullableRelation
    building_id: Optional[int]
    floor_id: Optional[int]
    project_id: Optional[int]

    def __str__(self) -> str:
        return self.global_id

    class Meta:
        table = "properties_property"


class PropertyRepo(BasePropertyRepo, CRUDMixin):
    """
    Репозиторий объекта недвижимости
    """

    model = Property
