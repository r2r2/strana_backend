from typing import Any

from common.orm.mixins import ReadWriteMixin
from common import cfields
from tortoise import Model, fields

from ..entities import BasePrivilegeRepo


class PrivilegeBenefit(Model):
    """
    Преимущества Программы привилегий
    """
    title: str = fields.CharField(description="Название", max_length=250)
    slug: str = fields.CharField(max_length=250, description='Slug', pk=True)
    is_active: bool = fields.BooleanField(description="Активность", default=True)
    priority = fields.IntField(description="Приоритет в подкатегории", default=0)
    image: dict[str, Any] | None = cfields.MediaField(
        description="Изображение", max_length=500, null=True
    )

    created_at = fields.DatetimeField(auto_now_add=True, description="Время создания")
    updated_at = fields.DatetimeField(auto_now=True, description="Время последнего обновления")

    class Meta:
        table = "privilege_benefit"

    def __repr__(self):
        return self.title


class PrivilegeBenefitRepo(BasePrivilegeRepo, ReadWriteMixin):
    """
    Репозиторий Преимуществ Программы привилегий
    """
    model = PrivilegeBenefit
