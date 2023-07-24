from typing import Any, Optional

from tortoise import Model, fields

from common import cfields
from common.orm.mixins import CRUDMixin
from src.dashboard.constants import WidthType
from src.dashboard.entities import BaseDashboardRepo


class Block(Model):
    """
    Блок
    """
    type: str = fields.CharField(max_length=255, null=True)
    width: int = cfields.IntChoiceField(choice_class=WidthType, description="Ширина блока", null=True)
    title: str = fields.CharField(max_length=255, null=True)
    description: str = fields.TextField(null=True)
    image: Optional[dict[str, Any]] = cfields.MediaField(
        description="Изображение", max_length=500, null=True
    )
    priority: int = fields.IntField(description="Приоритет", null=True)
    city: fields.ManyToManyRelation["City"] = fields.ManyToManyField(
        model_name="models.City",
        related_name="blocks",
        on_delete=fields.CASCADE,
        description="Город",
        through="dashboard_block_city_through",
        backward_key="block_id",
        forward_key="city_id",
    )

    created_at = fields.DatetimeField(auto_now_add=True, description="Время создания")
    updated_at = fields.DatetimeField(auto_now=True, description="Время последнего обновления")

    elements: fields.ReverseRelation["Element"]

    def __str__(self) -> str:
        return self.type

    class Meta:
        table = "dashboard_block"
        ordering = ["priority"]


class BlockRepo(BaseDashboardRepo, CRUDMixin):
    """
    Репозиторий блока
    """
    model = Block
