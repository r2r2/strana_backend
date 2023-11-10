from tortoise import fields

from common.orm.mixins import CRUDMixin
from ..entities import BasePaymentDatabaseModel, BasePaymentRepo


class PriceOfferMatrix(BasePaymentDatabaseModel):
    """
    Матрица предложения цены
    """
    id: int = fields.IntField(pk=True, description="ID")
    name = fields.CharField(max_length=100, null=True, description="Название")
    payment_method = fields.ForeignKeyField(
        model_name="models.PaymentMethod",
        on_delete=fields.CASCADE,
        related_name="price_offer",
        description="ИД предложения из ИК",
    )
    # guid обсудить
    by_dev: bool = fields.BooleanField(default=False, description="Субсидированная ипотека")
    price_type = fields.OneToOneField(
        model_name="models.PropertyPriceType",
        on_delete=fields.CASCADE,
        related_name="price_offer",
        description="Тип цены",
    )
    mortgage_type = fields.ForeignKeyField(
        model_name="models.MortgageType",
        on_delete=fields.CASCADE,
        related_name="mortgage_type",
        description="Тип ипотеки",
        null=True,
    )
    priority: int = fields.IntField(default=0, description="Приоритет")

    class Meta:
        table = "payments_price_offer_matrix"


class PriceOfferMatrixRepo(BasePaymentRepo, CRUDMixin):
    """
    Репозиторий матрицы предложения цены
    """
    model = PriceOfferMatrix
