from datetime import datetime
from typing import Any, Optional

from tortoise import Model, fields

from common import cfields
from common.orm.mixins import CRUDMixin
from src.dashboard.constants import WidthType
from src.dashboard.entities import BaseDashboardRepo


class Element(Model):
    """
    Элемент
    """
    type: str = fields.CharField(max_length=255)
    width: int = cfields.IntChoiceField(choice_class=WidthType, description="Ширина блока", null=True)
    title: str = fields.CharField(max_length=255, null=True)
    description: str = fields.TextField(null=True)
    image: Optional[dict[str, Any]] = cfields.MediaField(
        description="Изображение", max_length=500, null=True
    )
    expires: datetime = fields.DatetimeField(description="Время истечения", null=True)
    has_completed_booking: bool = fields.BooleanField(description="Бронирование завершено", null=True)
    priority: int = fields.IntField(description="Приоритет", default=0)

    block: fields.ForeignKeyRelation["Block"] = fields.ForeignKeyField(
        model_name="models.Block",
        related_name="elements",
        on_delete=fields.CASCADE,
        description="Блок",
        null=True,
    )
    city: fields.ManyToManyRelation["City"] = fields.ManyToManyField(
        model_name="models.City",
        related_name="elements",
        on_delete=fields.CASCADE,
        description="Город",
        through="dashboard_element_city_through",
        backward_key="element_id",
        forward_key="city_id",
    )
    created_at = fields.DatetimeField(auto_now_add=True, description="Время создания")
    updated_at = fields.DatetimeField(auto_now=True, description="Время последнего обновления")

    links: fields.ReverseRelation["Link"]

    def __str__(self) -> str:
        return self.type

    class Meta:
        table = "dashboard_element"


class ElementRepo(BaseDashboardRepo, CRUDMixin):
    """
    Репозиторий элемента
    """
    model = Element
