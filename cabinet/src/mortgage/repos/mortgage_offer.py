from tortoise import Model, fields

from common import orm
from common.orm.entities import BaseRepo
from common.orm.mixins import CRUDMixin


class MortgageOffer(Model):
    """
    Ипотечные предложения.
    """
    id: int = fields.IntField(description="ID", pk=True)
    name: str = fields.CharField(max_length=255, description="Название предложения")
    bank: fields.ForeignKeyNullableRelation["MortgageBank"] = fields.ForeignKeyField(
        model_name="models.MortgageBank",
        related_name="mortgage_offers",
        description="банк",
        null=True,
        on_delete=fields.CASCADE,
    )
    program: fields.ForeignKeyNullableRelation["MortgageProgram"] = fields.ForeignKeyField(
        model_name="models.MortgageProgram",
        related_name="mortgage_offers",
        description="ипотечная программа",
        null=True,
        on_delete=fields.CASCADE,
    )
    external_code: str = fields.TextField(description="Внешний код", null=True)
    monthly_payment: float = fields.FloatField(default=0, description="платеж в месяц")
    percent_rate: float = fields.FloatField(default=0, description="Процентная ставка")
    credit_term: float = fields.FloatField(default=0, description="Срок кредита")
    uid: str = fields.CharField(max_length=255, description="Для синхронизации с ДВИЖ", null=True)

    mortgage_dev_tickets: fields.ManyToManyRelation["MortgageDeveloperTicket"]

    class Meta:
        table = "mortgage_calculator_offer"


class MortgageOfferRepo(BaseRepo, CRUDMixin):
    """
    Репозиторий ипотечных программ и/к.
    """
    model = MortgageOffer
    a_builder: orm.AnnotationBuilder = orm.AnnotationBuilder(MortgageOffer)
