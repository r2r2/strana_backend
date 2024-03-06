from common.orm.mixins import ReadWriteMixin
from tortoise import Model, fields

from ..entities import BasePrivilegeRepo


class PrivilegeCooperationType(Model):
    """
    Виды сотрудничества программы привилегий
    """
    slug: str = fields.CharField(max_length=250, description='Slug', pk=True)
    title: str = fields.CharField(description="Название", max_length=250)
    is_active: bool = fields.BooleanField(description="Активность", default=True)

    created_at = fields.DatetimeField(auto_now_add=True, description="Время создания")
    updated_at = fields.DatetimeField(auto_now=True, description="Время последнего обновления")

    class Meta:
        table = "privilege_cooperation_type"


class PrivilegeCooperationTypeRepo(BasePrivilegeRepo, ReadWriteMixin):
    """
    Репозиторий Программ привилегий
    """
    model = PrivilegeCooperationType
