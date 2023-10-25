from tortoise import fields

from common.orm.mixins import CRUDMixin
from ..entities import BasePaymentDatabaseModel, BasePaymentRepo


class PriceSchema(BasePaymentDatabaseModel):
    """
    Схема сопоставление цен в матрице
    """

    id: int = fields.IntField(pk=True, description="ID")
    price_type = fields.ForeignKeyField(
        model_name="models.PropertyPriceType",
        on_delete=fields.CASCADE,
        related_name="price_schema",
        description="Тип цены",
    )
    slug = fields.CharField(
        max_length=15,
        null=True,
        unique=True,
        description="slug поля цены из Profit base",
    )

    class Meta:
        table = "payments_price_schema"


class PriceSchemaRepo(BasePaymentRepo, CRUDMixin):
    """
    Репозиторий схемы сопоставление цен в матрице
    """

    model = PriceSchema
