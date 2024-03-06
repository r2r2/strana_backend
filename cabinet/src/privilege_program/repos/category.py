from typing import Any

from common import cfields
from common.orm.mixins import ReadWriteMixin
from tortoise import Model, fields

from ..entities import BasePrivilegeRepo


class PrivilegeCategory(Model):
    """
    Категория программ привилегий

    """
    slug: str = fields.CharField(max_length=250, description='Slug', pk=True)
    title: str = fields.CharField(description="Название", max_length=250)
    is_active: bool = fields.BooleanField(description="Активность", default=True)
    dashboard_priority = fields.IntField(description="Приоритет на дашборде", default=0)
    filter_priority = fields.IntField(description="Приоритет в фильтре", default=0)
    cities: fields.ManyToManyRelation["City"] = fields.ManyToManyField(
        model_name="models.City",
        related_name="privilege_categories",
        through="privilege_category_m2m_city",
        description="Города",
        null=True,
        on_delete=fields.CASCADE,
        backward_key="privilege_category_id",
        forward_key="city_id",
    )
    image: dict[str, Any] | None = cfields.MediaField(
        description="Изображение", max_length=500, null=True
    )
    display_type: str = fields.CharField(max_length=250, null=True)

    created_at = fields.DatetimeField(auto_now_add=True, description="Время создания")
    updated_at = fields.DatetimeField(auto_now=True, description="Время последнего обновления")

    subcategories: fields.ReverseRelation["PrivilegeSubCategory"]

    class Meta:
        table = "privilege_category"

    def __repr__(self):
        return self.title


class PrivilegeSubCategory(Model):
    """
    Подкатегория программ привилегий

    """
    slug: str = fields.CharField(max_length=250, description='Слаг', pk=True)
    title: str = fields.CharField(description="Название", max_length=250)
    category = fields.ForeignKeyField(
        model_name="models.PrivilegeCategory",
        related_name="subcategories",
        to_field="slug",
        null=True,
        on_delete=fields.CASCADE,
    )
    is_active: bool = fields.BooleanField(description="Активность", default=True)

    created_at = fields.DatetimeField(auto_now_add=True, description="Время создания")
    updated_at = fields.DatetimeField(auto_now=True, description="Время последнего обновления")

    class Meta:
        table = "privilege_subcategory"


class PrivilegeCategoryRepo(BasePrivilegeRepo, ReadWriteMixin):
    """
    Репозиторий категорий привилегий
    """
    model = PrivilegeCategory


class PrivilegeSubCategoryRepo(BasePrivilegeRepo, ReadWriteMixin):
    """
    Репозиторий подкатегорий привилегий
    """
    model = PrivilegeSubCategory


class PrivilegeCategoryM2MCity(Model):
    """
    Отношения Категорий Программы привилегий к городам.
    """
    privilege_category: fields.ForeignKeyRelation[PrivilegeCategory] = fields.ForeignKeyField(
        model_name="models.PrivilegeCategory",
        related_name="privilege_category_m2m_city",
        description="Категории",
        to_field="slug",
        on_delete=fields.CASCADE,
    )
    city: fields.ForeignKeyRelation["City"] = fields.ForeignKeyField(
        model_name="models.City",
        related_name="privilege_category_m2m_city",
        description="Города",
        on_delete=fields.CASCADE,
    )

    class Meta:
        table = "privilege_category_m2m_city"
