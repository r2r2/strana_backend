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
    profitbase_id: Optional[int] = fields.IntField(
        description="Profitbase ID", null=True
    )
    type: Optional[str] = cfields.CharChoiceField(
        # todo: deprecated , use property_type
        description="Тип", max_length=50, null=True, choice_class=PropertyTypes
    )
    property_type: Optional[str] = fields.ForeignKeyField(
        description="Тип (модель)",
        model_name="models.PropertyType",
        related_name="properties",
        on_delete=fields.SET_NULL,
        null=True,
    )
    article: Optional[str] = fields.CharField(description="Артикул", max_length=50, null=True)
    plan: Annotated[str, Field(max_length=500)] = cfields.MediaField(
        description="Планировка", max_length=500, null=True
    )
    plan_png: Annotated[str, Field(max_length=500)] = cfields.MediaField(
        description="Планировка png", max_length=500, null=True
    )
    plan_hover: Optional[str] = fields.TextField(description="Обводка на плане", null=True)
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
    section: fields.ForeignKeyNullableRelation["BuildingSection"] = fields.ForeignKeyField(
        "models.BuildingSection", null=True, on_delete=fields.CASCADE, related_name="property_section"
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

    property_features: fields.ManyToManyRelation["Feature"]
    profitbase_plan: str = fields.CharField(description="План из Profitbase", max_length=512, null=True)

    is_angular: bool = fields.BooleanField(description="Квартира угловая?", default=False)
    balconies_count: Optional[int] = fields.IntField(description="Количество балконов", null=True)
    is_bathroom_window: bool = fields.BooleanField(description="Окно в ванной", default=False)
    master_bedroom: bool = fields.BooleanField(description="Мастер-спальня", default=False)
    window_view_profitbase: Optional[str] = fields.CharField(
        description="Вид из окна Profitbase",
        max_length=100,
        null=True)
    ceil_height: Optional[str] = fields.CharField(description="Высота потолка из Profitbase", max_length=16, null=True)
    is_cityhouse: bool = fields.BooleanField(description="Ситихаусы", default=False)
    corner_windows: bool = fields.BooleanField(description="Угловые окна", default=False)
    open_plan: bool = fields.BooleanField(description="Свободная планировка", default=False)
    frontage: bool = fields.BooleanField(description="Палисадник", default=False)
    has_high_ceiling: bool = fields.BooleanField(description="Высокие потолки", default=False)
    is_euro_layout: bool = fields.BooleanField(description="Европланировка", default=False)
    is_studio: bool = fields.BooleanField(description="Студия?", default=False)
    loggias_count: Optional[int] = fields.IntField(description="Количество лоджей", null=True)
    has_panoramic_windows: bool = fields.BooleanField(description="Панорамные окна", default=False)
    has_parking: bool = fields.BooleanField(description="Парковка", default=False)
    is_penthouse: bool = fields.BooleanField(description="Пентхаус", default=False)
    furnish_price_per_meter: Optional[Decimal] = fields.DecimalField(
        max_digits=14,
        decimal_places=2,
        null=True,
        description="Цена с отделкой за метр"
    )
    is_discount_enable: bool = fields.BooleanField(description="Скидка?", default=False)
    profitbase_property_status: Optional[str] = fields.CharField(
        description="Статус из Profitbase",
        max_length=64,
        null=True)
    smart_house: bool = fields.BooleanField(description="Умный дом", default=False)
    has_terrace: bool = fields.BooleanField(description="Терраса", default=False)
    has_two_sides_windows: bool = fields.BooleanField(description="Окна на 2 стороны", default=False)
    view_park: bool = fields.BooleanField(description="Вид на парк", default=False)
    view_river: bool = fields.BooleanField(description="Вид на реку", default=False)
    view_square: bool = fields.BooleanField(description="Вид на сквер", default=False)
    wardrobes_count: Optional[int] = fields.IntField(description="Количество гардеробных", null=True)
    profitbase_booked_until_date: Optional[str] = fields.CharField(
        description="Дата окончания брони из Profitbase",
        max_length=64,
        null=True)
    cash_price: Optional[Decimal] = fields.DecimalField(
        description="Цена за наличные", max_digits=14, decimal_places=2, null=True
    )

    def __str__(self) -> str:
        return self.global_id

    class Meta:
        table = "properties_property"


class PropertyRepo(BasePropertyRepo, CRUDMixin):
    """
    Репозиторий объекта недвижимости
    """

    model = Property
