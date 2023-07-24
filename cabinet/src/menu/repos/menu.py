from typing import Optional, Any

from tortoise import Model, fields

from common import cfields
from common.orm.mixins import ReadWriteMixin, CountMixin
from src.cities.repos import City
from src.menu.entities import BaseMenuRepo
from src.users.repos import UserRole


class Menu(Model):
    """
    Фиксирует список пунктов бокового меню. Используется 1 инфоблок по ЛК Брокера и ЛК Клиента
    """
    id: int = fields.BigIntField(description="ID", pk=True, index=True)
    name: str = fields.CharField(description="Название пункта меню", null=False, max_length=15)
    link: str = fields.CharField(description="Ссылка пункта меню", null=False, max_length=50)
    priority: int = fields.IntField(description="Приоритет (чем меньше чем, тем раньше)", null=False)
    cities: fields.ManyToManyRelation["City"] = fields.ManyToManyField(
        description="Города",
        model_name='models.City',
        through="menus_menu_cities",
        backward_key="menu_city_id",
        forward_key="city_id",
        related_name="menu_cities",
    )
    icon: Optional[dict[str, Any]] = cfields.MediaField(
        description="Файл", max_length=300, null=True
    )
    roles = fields.ManyToManyField(
        description="Роли",
        model_name='models.UserRole',
        through="menus_menu_roles",
        backward_key="menu_role_id",
        forward_key="role_id",
        related_name="menu_roles",
    )
    hide_desktop: bool = fields.BooleanField(description="Скрывать на мобильной версии", default=False)

    class Meta:
        table = "menus_menu"
        ordering = ["priority"]


class MenuRepo(BaseMenuRepo, ReadWriteMixin, CountMixin):
    """
    Репозиторий уведомления
    """
    model = Menu
