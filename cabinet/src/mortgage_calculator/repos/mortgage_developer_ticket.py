from tortoise import Model, fields

from common.orm.entities import BaseRepo
from common.orm.mixins import CRUDMixin


class MortgageDeveloperTicket(Model):
    """
    Заявка через застройщика.
    """

    id: int = fields.IntField(description="ID", pk=True)

    proposals_issued: fields.ManyToManyRelation["MortgageSubmittedProposal"] = fields.ManyToManyField(  # Entity
        model_name="models.MortgageSubmittedProposal",
        related_name="mortgage_calculator_dev_ticket",
        through="mortgage_calculator_dev_ticket_proposal_through",
        description="Выбранные предложения",
        null=True,
        on_delete=fields.CASCADE,
        backward_key="mortgage_dev_ticket_id",
        forward_key="mortgage_proposal_id",
    )

    developer_ticket_statuses: fields.ManyToManyRelation["MortgageApplicationStatus"] = fields.ManyToManyField(
        # Entity
        model_name="models.MortgageApplicationStatus",
        related_name="mortgage_calculator_dev_ticket",
        through="mortgage_calculator_ticket_status_through",
        description="Статус заявки",
        null=True,
        on_delete=fields.CASCADE,
        backward_key="mortgage_dev_application_id",
        forward_key="mortgage_status_id",
    )

    calculator_condition: fields.ManyToManyRelation["MortageCalculatorCondition"] = fields.ManyToManyField(  # Entity
        model_name="models.MortageCalculatorCondition",
        related_name="mortgage_calculator_dev_ticket",
        through="mortgage_calculator_dev_ticket_condition_through",
        description="Условия в калькуляторе",
        null=True,
        on_delete=fields.CASCADE,
        backward_key="mortgage_dev_ticket_id",
        forward_key="mortgage_condition_id",
    )

    ticket: fields.ManyToManyRelation["MortgageTicket"] = fields.ManyToManyField(  # Entity
        model_name="models.MortgageTicket",
        related_name="mortgage_calculator_dev_ticket",
        through="mortgage_calculator_dev_ticket_to_ticket_through",
        description="Заявка на ипотеку",
        null=True,
        on_delete=fields.CASCADE,
        backward_key="mortgage_dev_ticket_id",
        forward_key="mortgage_ticket_id",
    )

    ticket_condition: fields.ManyToManyRelation["MortgageConditionMatrix"] = fields.ManyToManyField(  # Entity
        model_name="models.MortgageConditionMatrix",
        related_name="mortgage_calculator_dev_ticket",
        through="mortgage_calculator_dev_ticket_condition_through",
        description="Условия подачи заявки",
        null=True,
        on_delete=fields.CASCADE,
        backward_key="mortgage_dev_ticket_id",
        forward_key="mortgage_condition_id",
    )

    mortage_form_data: fields.ManyToManyRelation["MortgageForm"] = fields.ManyToManyField(  # Entity
        model_name="models.MortgageForm",
        related_name="mortgage_calculator_dev_ticket",
        through="mortgage_calculator_dev_ticket_form_through",
        description="Данные с формы",
        null=True,
        on_delete=fields.CASCADE,
        backward_key="mortgage_dev_ticket_id",
        forward_key="mortgage_form_id",
    )

    def __str__(self) -> str:
        return self.id

    class Meta:
        table = "mortgage_calculator_developer_ticket"


# class MortgageDeveloperTicketProposalThrough(Model):
#     """
#     Выбранные предложения.
#     """
#     id: int = fields.IntField(description="ID", pk=True)
#     mortgage_dev_application_id: fields.ForeignKeyRelation[MortgageDeveloperTicket] = fields.ForeignKeyField(
#         model_name="models.MortgageDeveloperTicket",
#         related_name="mortgage_dev_ticket_proposal_through",
#         description="Заявка",
#         on_delete=fields.CASCADE,
#     )
#     mortgage_proposal_id: fields.ForeignKeyRelation["MortgageSubmittedProposal"] = fields.ForeignKeyField(
#         model_name="models.MortgageSubmittedProposal",
#         related_name="mortgage_proposal_dev_ticket_through",
#         description="Предложение",
#         on_delete=fields.CASCADE,
#     )

#     class Meta:
#         table = "mortgage_calсutator_dev_ticket_proposal_through"


class MortgageDeveloperTicketRepo(BaseRepo, CRUDMixin):
    """
    Репозиторий заявки через застройщика.
    """

    model = MortgageDeveloperTicket
