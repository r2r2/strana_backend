from tortoise import fields

from common.orm.mixins import CRUDMixin
from ..entities import BasePaymentDatabaseModel, BasePaymentRepo


class PriceImportMatrix(BasePaymentDatabaseModel):
    """
    Матрица сопоставления цен при импорте объекта
    """

    id: int = fields.IntField(pk=True, description="ID")
    cities = fields.ManyToManyField(
        model_name="models.City",
        through="payments_price_import_matrix_cities",
        backward_key="import_price_id",
        forward_key="city_id",
        related_name="cities",
        description="Города",
    )
    price_schema = fields.ForeignKeyField(
        model_name="models.PriceSchema",
        on_delete=fields.CASCADE,
        related_name="price_schema",
        description="Сопоставление цен",
    )
    default: bool = fields.BooleanField(default=False, description="По умолчанию")

    class Meta:
        table = "payments_price_import_matrix"


class PriceImportMatrixRepo(BasePaymentRepo, CRUDMixin):
    """
    Репозиторий матрицы сопоставления цен при импорте объекта
    """

    model = PriceImportMatrix
