from typing import Any

from common.orm.mixins import ReadWriteMixin
from common import cfields
from tortoise import Model, fields

from ..entities import BasePrivilegeRepo

class PrivilegeInfo(Model):
    """
    Общая информация Программы привилегий
    """
    title: str = fields.CharField(description="Название", max_length=250)
    slug: str = fields.CharField(max_length=250, description='Slug', pk=True)
    description: str = fields.TextField(description="Описание")
    image: dict[str, Any] | None = cfields.MediaField(
        description="Изображение", max_length=500, null=True
    )

    created_at = fields.DatetimeField(auto_now_add=True, description="Время создания")
    updated_at = fields.DatetimeField(auto_now=True, description="Время последнего обновления")

    class Meta:
        table = "privilege_info"

    def __repr__(self):
        return self.title


class PrivilegeInfoRepo(BasePrivilegeRepo, ReadWriteMixin):
    """
    Репозиторий Общей информации Программы привилегий
    """
    model = PrivilegeInfo
