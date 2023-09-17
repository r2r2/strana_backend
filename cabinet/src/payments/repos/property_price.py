from tortoise import fields

from common.orm.mixins import CRUDMixin
from ..entities import BasePaymentDatabaseModel, BasePaymentRepo


class PropertyPriceType(BasePaymentDatabaseModel):
    """
    Тип цены объекта недвижимости
    """
    id: int = fields.IntField(pk=True, description="ID")
    name = fields.CharField(max_length=100, null=True, description="Название")
    default: bool = fields.BooleanField(default=False, description="Тип по умолчанию")
    slug = fields.CharField(max_length=15, null=True, unique=True, description="slug для импорта с портала")

    class Meta:
        table = "payments_property_price_type"


class PropertyPriceTypeRepo(BasePaymentRepo, CRUDMixin):
    """
    Репозиторий типа цены объекта недвижимости
    """
    model = PropertyPriceType


class PropertyPrice(BasePaymentDatabaseModel):
    """
    Цена объекта недвижимости
    """
    id: int = fields.IntField(description="ID", pk=True)
    price = fields.DecimalField(description="Цена", max_digits=10, decimal_places=2, null=True)
    price_type = fields.ForeignKeyField(
        model_name="models.PropertyPriceType",
        on_delete=fields.CASCADE,
        related_name="type",
        description="Тип цены",
    )

    class Meta:
        table = "payments_property_price"


class PropertyPriceRepo(BasePaymentRepo, CRUDMixin):
    """
    Репозиторий цены объекта недвижимости
    """
    model = PropertyPrice
