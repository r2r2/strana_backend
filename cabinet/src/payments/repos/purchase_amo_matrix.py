from tortoise import fields

from common.orm.mixins import CRUDMixin
from ..entities import BasePaymentDatabaseModel, BasePaymentRepo


class PurchaseAmoMatrix(BasePaymentDatabaseModel):
    """
    Матрица способов оплаты при взаимодействии с АМО.
    """

    id: int = fields.IntField(pk=True, description="ID")
    payment_method = fields.ForeignKeyField(
        model_name="models.PaymentMethod",
        on_delete=fields.CASCADE,
        related_name="purchase_amo_matrix",
        description="Способ оплаты",
    )
    mortgage_type = fields.ForeignKeyField(
        model_name="models.MortgageType",
        on_delete=fields.CASCADE,
        related_name="purchase_amo_matrix",
        description="Тип ипотеки",
        null=True,
    )
    amo_payment_type = fields.IntField(description="ID Значения в АМО для типа оплаты")
    default: bool = fields.BooleanField(default=False, description="По умолчанию")
    priority: int = fields.IntField(default=0, description="Приоритет")

    class Meta:
        table = "payments_purchase_amo_matrix"


class PurchaseAmoMatrixRepo(BasePaymentRepo, CRUDMixin):
    """
    Репозиторий матрицы способов оплаты при взаимодействии с АМО.
    """

    model = PurchaseAmoMatrix
