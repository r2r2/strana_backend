from typing import Any, Optional

from common import cfields
from common.models import TimeBasedMixin
from common.orm.entities import BaseRepo
from common.orm.mixins import ListMixin
from tortoise import Model, fields


class MainPageOffer(Model, TimeBasedMixin):
    """
    Блок: что мы предлагаем
    """
    id: int = fields.IntField(description="ID", pk=True)
    title: str = fields.TextField(max_length=255, description="Заголовок")
    description: str = fields.TextField(description="Описание")
    image: Optional[dict[str, Any]] = cfields.MediaField(
        description="Изображение", max_length=500, null=True
    )
    priority: int = fields.IntField(description="Приоритет", default=0)
    is_active: bool = fields.BooleanField(description="Активность", default=True)

    class Meta:
        table = "main_page_offer"
        ordering = ["-priority"]


class MainPageOfferRepo(BaseRepo, ListMixin):
    """
    Репозиторий блока "Что мы предлагаем" главной страницы
    """
    model = MainPageOffer
