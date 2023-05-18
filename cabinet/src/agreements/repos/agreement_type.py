from typing import Optional

from common.models import TimeBasedMixin
from common.orm.mixins import CountMixin, CRUDMixin
from tortoise import Model, fields

from ..entities import BaseAgreementRepo


class AgreementType(Model, TimeBasedMixin):
    """
    Типы договоров
    """
    id: int = fields.IntField(description="ID", pk=True, index=True)
    name: str = fields.CharField(description="Название типа", max_length=100)
    description: Optional[str] = fields.TextField(description="Описание статуса", null=True)
    priority: int = fields.IntField(description="Приоритет вывода")
    created_by: fields.ForeignKeyNullableRelation["User"] = fields.ForeignKeyField(
        model_name="models.User",
        description='Кем создано',
        on_delete=fields.SET_NULL,
        related_name="created_agreement_types",
        null=True,
    )
    updated_by: fields.ForeignKeyNullableRelation["User"] = fields.ForeignKeyField(
        model_name="models.User",
        description='Кем изменено',
        on_delete=fields.SET_NULL,
        related_name="updated_agreement_types",
        null=True,
    )

    class Meta:
        table = "agreement_type"


class AgreementTypeRepo(BaseAgreementRepo, CRUDMixin, CountMixin):
    """
    Репозиторий типа договора
    """
    model = AgreementType
