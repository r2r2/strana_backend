from common.models import TimeBasedMixin
from common.orm.entities import BaseRepo
from common.orm.mixins import ListMixin
from tortoise import Model, fields


class MainPageSellOnline(Model, TimeBasedMixin):
    """
    Блок: Продавайте online
    """
    id: int = fields.IntField(description="ID", pk=True)
    title: str = fields.TextField(max_length=255, description="Заголовок")
    description: str = fields.TextField(description="Описание")
    priority: int = fields.IntField(description="Приоритет", default=0)
    is_active: bool = fields.BooleanField(description="Активность", default=True)

    class Meta:
        table = "main_page_sell_online"
        ordering = ["-priority"]


class MainPageSellOnlineRepo(BaseRepo, ListMixin):
    """
    Репозиторий блока "Продавайте online" главной страницы
    """
    model = MainPageSellOnline
