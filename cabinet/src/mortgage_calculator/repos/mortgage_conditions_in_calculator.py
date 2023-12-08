from datetime import datetime

from tortoise import Model, fields

from common import cfields
from common.orm.entities import BaseRepo
from common.orm.mixins import CRUDMixin
from ..constants import ProofOfIncome


class MortageCalculatorCondition(Model):
    """
    Условия калькулятора.
    """
    id: int = fields.IntField(description="ID", pk=True)

    cost_before: float = fields.FloatField(description="Стоимость до")
    initial_fee_before: float = fields.FloatField(description="Первоначальный взнос до")
    until: float = fields.FloatField(description="Срок до")

    mortage_program: fields.ManyToManyRelation["MortgageProgram"] = fields.ManyToManyField(  # Entity
        model_name="models.MortgageProgram",
        related_name="mortgagecondition_program",
        through="mortgage_calculator_condition_program_through",
        description="ипотечные программы",
        null=True,
        on_delete=fields.CASCADE,
        backward_key="mortgage_condition_id",
        forward_key="mortgage_program_id",
    )

    mortage_bank: fields.ManyToManyRelation["MortgageBank"] = fields.ManyToManyField(  # Entity
        model_name="models.MortgageBank",
        related_name="mortgagecondition_bank",
        through="mortgage_calculator_condition_bank_through",
        description="банки",
        null=True,
        on_delete=fields.CASCADE,
        backward_key="mortgage_condition_id",
        forward_key="mortgage_bank_id",
    )

    created_at: datetime = fields.DatetimeField(
        description="Дата и время создания", auto_now_add=True
    )

    proof_of_income: str = cfields.CharChoiceField(
        description="Подтверждение дохода",
        max_length=50,
        default=ProofOfIncome.CASE,
        choice_class=ProofOfIncome,
    )

    def __str__(self) -> str:
        return self.id

    class Meta:
        table = "mortgage_calcutator_condition"


class MortgageConditionBankThrough(Model):
    """
    Отношения ип калькулят условий к банкам.
    """
    id: int = fields.IntField(description="ID", pk=True)
    mortgagecondition_id: fields.ForeignKeyRelation[MortageCalculatorCondition] = fields.ForeignKeyField(
        model_name="models.MortageCalculatorCondition",
        related_name="mortgage_condition_bank_through",
        description="Условия",
        on_delete=fields.CASCADE,
    )
    mortgagebank_id: fields.ForeignKeyRelation["MortgageBank"] = fields.ForeignKeyField(
        model_name="models.MortgageBank",
        related_name="mortgage_bank_condition_through",
        description="Банки",
        on_delete=fields.CASCADE,
    )

    class Meta:
        table = "mortgage_calсutator_condition_bank_through"


class MortgageConditionProgramThrough(Model):
    """
    Отношения им калькулят условий к программам.
    """
    id: int = fields.IntField(description="ID", pk=True)
    mortgagecondition_id: fields.ForeignKeyRelation[MortageCalculatorCondition] = fields.ForeignKeyField(
        model_name="models.MortageCalculatorCondition",
        related_name="mortgage_condition_program_through",
        description="Условия",
        on_delete=fields.CASCADE,
    )
    mortgageprogram_id: fields.ForeignKeyRelation["MortgageProgram"] = fields.ForeignKeyField(
        model_name="models.MortgageProgram",
        related_name="mortgage_зrogram_condition_through",
        description="Программы",
        on_delete=fields.CASCADE,
    )

    class Meta:
        table = "mortgage_calсutator_condition_program_through"


class MortageCalculatorConditionRepo(BaseRepo, CRUDMixin):
    """
    Репозиторий условий и/к .
    """
    model = MortageCalculatorCondition
