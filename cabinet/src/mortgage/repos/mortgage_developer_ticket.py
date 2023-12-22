from tortoise import Model, fields

from common.orm.entities import BaseRepo
from common.orm.mixins import CRUDMixin


class MortgageDeveloperTicket(Model):
    """
    Заявка через застройщика.
    """

    id: int = fields.IntField(description="ID", pk=True)

    offers: fields.ManyToManyRelation["MortgageOffer"] = fields.ManyToManyField(
        model_name="models.MortgageOffer",
        related_name="mortgage_dev_tickets",
        through="mortgage_calculator_dev_ticket_offer_through",
        description="Выбранные предложения",
        null=True,
        on_delete=fields.CASCADE,
        backward_key="mortgage_dev_ticket_id",
        forward_key="mortgage_offer_id",
    )
    status: fields.ForeignKeyRelation["MortgageApplicationStatus"] = fields.ForeignKeyField(
        model_name="models.MortgageApplicationStatus",
        related_name="mortgage_dev_ticket",
        description="Статус заявки",
        null=True,
        on_delete=fields.CASCADE,
    )
    calculator_condition: fields.ForeignKeyNullableRelation["MortageCalculatorCondition"] = fields.ForeignKeyField(
        model_name="models.MortgageCalculatorCondition",
        related_name="mortgage_dev_ticket",
        description="Условие в калькуляторе",
        null=True,
        on_delete=fields.CASCADE,
    )
    form_data: fields.ForeignKeyNullableRelation["MortgageForm"] = fields.ForeignKeyField(
        model_name="models.MortgageForm",
        related_name="mortgage_dev_ticket",
        description="Данные с формы",
        null=True,
        on_delete=fields.CASCADE,
    )
    booking: fields.ForeignKeyRelation["Booking"] = fields.ForeignKeyField(
        model_name="models.Booking",
        related_name="mortgage_dev_tickets",
        on_delete=fields.CASCADE,
    )

    def __str__(self) -> str:
        return f"Заявка через застройщика. {self.id}"

    class Meta:
        table = "mortgage_calculator_developer_ticket"


class MortgageDeveloperTicketOfferThrough(Model):
    """
    Выбранные предложения.
    """
    id: int = fields.IntField(description="ID", pk=True)
    mortgage_dev_ticket: fields.ForeignKeyRelation[MortgageDeveloperTicket] = fields.ForeignKeyField(
        model_name="models.MortgageDeveloperTicket",
        related_name="mortgage_dev_ticket_offer_through",
        description="Заявка",
        on_delete=fields.CASCADE,
    )
    mortgage_offer: fields.ForeignKeyRelation["MortgageOffer"] = fields.ForeignKeyField(
        model_name="models.MortgageOffer",
        related_name="mortgage_offer_dev_ticket_through",
        description="Предложение",
        on_delete=fields.CASCADE,
    )

    class Meta:
        table = "mortgage_calculator_dev_ticket_offer_through"


class MortgageDeveloperTicketRepo(BaseRepo, CRUDMixin):
    """
    Репозиторий заявки через застройщика.
    """

    model = MortgageDeveloperTicket
