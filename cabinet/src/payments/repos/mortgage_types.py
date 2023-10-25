from tortoise import fields

from common.orm.mixins import CRUDMixin
from ..entities import BasePaymentDatabaseModel, BasePaymentRepo


class MortgageType(BasePaymentDatabaseModel):
    """
    Тип ипотеки
    """

    id: int = fields.IntField(pk=True, description="ID")
    title = fields.CharField(max_length=100, null=True, description="Название")
    amocrm_id: int | None = fields.BigIntField(
        description="ID в AmoCRM", null=True, unique=True
    )

    class Meta:
        table = "payments_mortgage_types"


class MortgageTypeRepo(BasePaymentRepo, CRUDMixin):
    """
    Репозиторий типа ипотек
    """

    model = MortgageType
