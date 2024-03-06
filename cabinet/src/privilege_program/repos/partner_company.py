from typing import Any

from common import cfields
from common.orm.mixins import ReadWriteMixin
from tortoise import Model, fields

from ..entities import BasePrivilegeRepo


class PrivilegePartnerCompany(Model):
    """
    Компания-Партнёр программы привилегий
    """
    title: str = fields.CharField(description="Название", max_length=250)
    slug: str = fields.CharField(max_length=250, description='Slug', pk=True)
    description: str = fields.TextField(description="Описание")
    link: str = fields.CharField(max_length=250, description="Ссылка на сайт")
    image: dict[str, Any] | None = cfields.MediaField(
        description="Изображение", max_length=500, null=True
    )

    created_at = fields.DatetimeField(auto_now_add=True, description="Время создания")
    updated_at = fields.DatetimeField(auto_now=True, description="Время последнего обновления")

    class Meta:
        table = "privilege_company"

    def __repr__(self):
        return self.slug


class PrivilegePartnerCompanyRepo(BasePrivilegeRepo, ReadWriteMixin):
    """
    Репозиторий Компаний-Партнёров программы привилегий
    """

    model = PrivilegePartnerCompany
