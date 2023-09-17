from typing import Any, Optional

from common import cfields
from common.models import TimeBasedMixin
from common.orm.entities import BaseRepo
from common.orm.mixins import ListMixin
from tortoise import Model, fields


class MainPagePartnerLogo(Model, TimeBasedMixin):
    """
    Блок: логотипы партнеров
    """
    id: int = fields.IntField(description="ID", pk=True)
    image: Optional[dict[str, Any]] = cfields.MediaField(
        description="Изображение", max_length=500, null=True
    )
    priority: int = fields.IntField(description="Приоритет", default=0)
    is_active: bool = fields.BooleanField(description="Активность", default=True)

    class Meta:
        table = "main_page_partner_logo"
        ordering = ["priority"]


class MainPagePartnerLogoRepo(BaseRepo, ListMixin):
    """
    Репозиторий логотипов партнёров на главной страницы
    """
    model = MainPagePartnerLogo
