from typing import Optional, Any, Union

from tortoise.query_utils import Q, Prefetch

from common import cfields

from tortoise import Model, fields

from common.orm.mixins import ListMixin, UpdateOrCreateMixin, CreateMixin
from ..entities import BaseTipRepo


class Tip(Model):
    """
    Подсказка
    """

    id: int = fields.IntField(description="ID", pk=True)
    text: Optional[str] = fields.TextField(description="Текст", null=True)
    title: Optional[str] = fields.CharField(description="Заголовок", max_length=200, null=True)
    image: Optional[dict[str, Any]] = cfields.MediaField(
        description="Изображение", max_length=500, null=True
    )
    order: Optional[int] = fields.IntField(description="Порядок", null=True)
    order_test: Optional[int] = fields.IntField(description="Порядок", null=True)

    def __str__(self) -> str:
        return self.title if self.title else str(self.id)

    class Meta:
        table = "tips_tip"
        ordering = ("order",)


class TipRepo(BaseTipRepo, CreateMixin, UpdateOrCreateMixin, ListMixin):
    """
    Репозиторий подсказки
    """

    model = Tip
