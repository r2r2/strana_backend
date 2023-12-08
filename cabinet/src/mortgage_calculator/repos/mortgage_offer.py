from tortoise import Model, fields

from common.orm.entities import BaseRepo
from common.orm.mixins import CRUDMixin


class MortgageOffer(Model):
    """
    # Программы под ипотечный калькулятор.
    """
    id: int = fields.IntField(description="ID", pk=True)
    offer_name: str = fields.TextField(description="Названеи оффера")

    bank: fields.ManyToManyRelation["MortgageBank"] = fields.ManyToManyField(  # Entity
        model_name="models.MortgageBank",
        related_name="mortgageeoffer_bank",
        through="mortgage_calculator_offers_banks_through",
        description="банки",
        null=True,
        on_delete=fields.CASCADE,
        backward_key="mortgageoffer_id",
        forward_key="mortgagebank_id",
    )

    programs: fields.ManyToManyRelation["MortgageProgram"] = fields.ManyToManyField(  # Entity
        model_name="models.MortgageProgram",
        related_name="mortgageoffer_program",
        through="mortgage_calculator_offers_program_through",
        description="ипотечные программы",
        null=True,
        on_delete=fields.CASCADE,
        backward_key="mortgageoffer_id",
        forward_key="mortgageprogram_id",
    )

    external_code: str = fields.TextField(description="Внешний код")
    payment_per_month: int = fields.FloatField(default=0, description="платеж в месяц")
    interest_rate: int = fields.FloatField(default=0, description="Процентная ставка")
    credit_term: int = fields.FloatField(default=0, description="Срок кредита")

    class Meta:
        table = "mortgage_calculator_offer"


class MortgageOfferBankThrough(Model):
    """
    Проекты, для которых настроено уведомление о QR-коде для смс. #***
    """
    id: int = fields.IntField(description="ID", pk=True)
    mortgageoffer_id: fields.ForeignKeyRelation[MortgageOffer] = fields.ForeignKeyField(
        model_name="models.MortgageOffer",
        related_name="mortgage_offer_bank_through",
        description="Отношения банков",
        on_delete=fields.CASCADE,
    )
    mortgagebank_id: fields.ForeignKeyRelation["MortgageBank"] = fields.ForeignKeyField(
        model_name="models.MortgageBank",
        related_name="mortgage_bank_offer_through",
        description="Из офферов в банки",
        on_delete=fields.CASCADE,
    )

    class Meta:
        table = "mortgage_canlutator_offer_bank_through"


class MortgageOfferProgramThrough(Model):
    """
    Проекты, для которых настроено уведомление о QR-коде для смс. #***
    """
    id: int = fields.IntField(description="ID", pk=True)
    mortageoffer_id: fields.ForeignKeyRelation[MortgageOffer] = fields.ForeignKeyField(
        model_name="models.MortgageOffer",
        related_name="mortgage_offer_program_through",
        description="Оферта",
        on_delete=fields.CASCADE,
    )
    mortageprogram_id: fields.ForeignKeyRelation["MortgageProgram"] = fields.ForeignKeyField(
        model_name="models.MortgageProgram",
        related_name="mortgage_program_offer_through",
        description="Оферта программы",
        on_delete=fields.CASCADE,
    )

    class Meta:
        table = "mortgage_canlutator_offer_program_through"


class MortgageOfferRepo(BaseRepo, CRUDMixin):
    """
    # Репозиторий ипотечных программ и/к .
    """
    model = MortgageOffer
