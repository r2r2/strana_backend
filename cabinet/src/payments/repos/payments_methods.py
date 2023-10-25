from tortoise import fields

from common.orm.mixins import CRUDMixin
from ..entities import BasePaymentDatabaseModel, BasePaymentRepo


class PaymentMethod(BasePaymentDatabaseModel):
    """
    Способ оплаты
    """
    id: int = fields.IntField(pk=True, description="ID")
    name = fields.CharField(max_length=100, null=True, description="Название")
    amocrm_id: int | None = fields.BigIntField(description="ID в AmoCRM", null=True, unique=True)

    class Meta:
        table = "payments_payment_method"


class PaymentMethodRepo(BasePaymentRepo, CRUDMixin):
    """
    Репозиторий способа оплаты
    """
    model = PaymentMethod
