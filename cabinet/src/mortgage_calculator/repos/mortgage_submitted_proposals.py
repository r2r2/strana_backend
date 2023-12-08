from tortoise import Model, fields

from common.orm.entities import BaseRepo
from common.orm.mixins import CRUDMixin


class MortgageSubmittedProposal(Model):
    """
    Поданные предложения.
    """
    id: int = fields.IntField(description="ID", pk=True)
    mortgage_application: int = fields.IntField(description="Заявка ан ипотеку")
    name: str = fields.TextField(description="Название предложения")
    mortgage_offer: fields.ManyToManyRelation["MortgageOffer"] = fields.ManyToManyField(  # Entity
        model_name="models.MortgageOffer",
        related_name="mortgageproposal_offer",
        through="mortgage_calculator_proposal_offers_through",
        description="ипотечные предложения",
        null=True,
        on_delete=fields.CASCADE,
        backward_key="mortgage_proposal_id",
        forward_key="mortgage_offer_id",
    )
    external_code: str = fields.TextField(description="Внешний код")

    def __str__(self) -> str:
        return self.name

    class Meta:
        table = "mortgage_submitted_proposal"


class MortgageSubmittedProposalOfferThrough(Model):
    """
    Связь 
    """
    id: int = fields.IntField(description="ID", pk=True)
    mortgage_proposal_id: fields.ForeignKeyRelation[MortgageSubmittedProposal] = fields.ForeignKeyField(
        model_name="models.MortgageSubmittedProposal",
        related_name="mortgage_submitted_proposal_offer_through",
        description="Из поданных предложений в ип предложения",
        on_delete=fields.CASCADE,
    )
    mortgage_offer_id: fields.ForeignKeyRelation["MortgageOffer"] = fields.ForeignKeyField(
        model_name="models.MortgageOffer",
        related_name="mortgage_offer_submitted_proposal_through",
        description="Из ип предложений в поданные предложения",
        on_delete=fields.CASCADE,
    )

    class Meta:
        table = "mortgage_canlutator_submitted_proposal_offer_through"


class MortgageSubmittedProposalRepo(BaseRepo, CRUDMixin):
    """
    Репозиторий поданных предложений.
    """
    model = MortgageSubmittedProposal
