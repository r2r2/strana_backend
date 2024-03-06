from datetime import datetime

from common.orm.mixins import ReadWriteMixin
from tortoise import Model, fields

from ..entities import BasePrivilegeRepo


class PrivilegeProgram(Model):
    """
    Программа привилегий
    """
    slug: str = fields.CharField(max_length=250, description='Slug', pk=True)
    partner_company: fields.ForeignKeyRelation["PrivilegePartnerCompany"] = fields.ForeignKeyField(
        description="Компания-партнёр",
        model_name="models.PrivilegePartnerCompany",
        related_name="programs",
        on_delete=fields.CASCADE,
    )
    is_active: bool = fields.BooleanField(description="Активность", default=True)
    priority_in_subcategory = fields.IntField(description="Приоритет в подкатегории", default=0)
    until: datetime | None = fields.DatetimeField(description="Срок действия", null=True)
    cooperation_type: fields.ForeignKeyRelation["PrivilegeCooperationType"] = fields.ForeignKeyField(
        description="Вид сотрудничества",
        model_name="models.PrivilegeCooperationType",
        related_name="programs",
        to_field="slug",
        on_delete=fields.SET_NULL,
        null=True,
    )
    description: str = fields.TextField(description="Краткое описание")
    conditions: str = fields.TextField(description="Условия")
    promocode: str = fields.CharField(max_length=250, description="Промокод")
    promocode_rules: str = fields.TextField(description="Правила использования промокода")
    button_label: str = fields.CharField(max_length=250, description="Название кнопки")
    button_link: str = fields.CharField(max_length=250, description="Ссылка на кнопке")
    category = fields.ForeignKeyField(
        model_name="models.PrivilegeCategory",
        related_name="programs",
        to_field="slug",
        null=True,
        on_delete=fields.SET_NULL,
    )
    subcategory = fields.ForeignKeyField(
        model_name="models.PrivilegeSubCategory",
        related_name="programs",
        to_field="slug",
        null=True,
        on_delete=fields.SET_NULL,
    )
    created_at = fields.DatetimeField(auto_now_add=True, description="Время создания")
    updated_at = fields.DatetimeField(auto_now=True, description="Время последнего обновления")

    class Meta:
        table = "privilege_program"

    def __repr__(self):
        return self.slug


class PrivilegeProgramRepo(BasePrivilegeRepo, ReadWriteMixin):
    """
    Репозиторий Программ привилегий
    """
    model = PrivilegeProgram
