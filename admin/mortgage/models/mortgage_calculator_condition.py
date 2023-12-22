from datetime import datetime

from django.db import models
from django.utils.translation import gettext_lazy as _


class MortgageCalculatorCondition(models.Model):
    """
    Условия в калькуляторе.
    """
    class ProofOfIncome(models.TextChoices):
        """
        Выборочное подтверждение прихода
        """
        NO_REFERENCES = "no_references", _("Без справок")

    cost_before: float = models.FloatField(verbose_name="Стоимость до", null=True, blank=True)
    initial_fee_before: float = models.FloatField(verbose_name="Первоначальный взнос до", null=True, blank=True)
    until: float = models.FloatField(verbose_name="Срок до", null=True, blank=True)
    programs: models.ManyToManyField = models.ManyToManyField(
        verbose_name="Ипотечные программы",
        to="mortgage.MortgageProgram",
        through="MortgageConditionProgramThrough",
        through_fields=("mortgage_condition", "mortgage_program"),
        related_name="mortgage_conditions",
        blank=True,
    )
    banks: models.ManyToManyField = models.ManyToManyField(
        verbose_name="Банки",
        to="mortgage.MortgageBank",
        through="MortgageConditionBankThrough",
        through_fields=("mortgage_condition", "mortgage_bank"),
        related_name="mortgage_conditions",
        blank=True,
    )
    proof_of_income: str = models.CharField(
        verbose_name="Подтверждение дохода",
        max_length=50,
        choices=ProofOfIncome.choices,
        null=True,
        blank=True,
    )
    created_at: datetime = models.DateTimeField(
        verbose_name="Дата и время создания", auto_now_add=True
    )

    def __str__(self) -> str:
        return f"Условие в калькуляторе {self.id}"

    class Meta:
        managed = False
        db_table = 'mortgage_calculator_condition'
        verbose_name = "Условие в калькуляторе"
        verbose_name_plural = "21.4 Условия в калькуляторе"


class MortgageConditionProgramThrough(models.Model):
    """
    Отношения ип калькулят условий к программам.
    """
    mortgage_condition: models.ForeignKey = models.ForeignKey(
        to="mortgage.MortgageCalculatorCondition",
        on_delete=models.CASCADE,
        related_name='mortgage_condition_program_through',
    )
    mortgage_program: models.ForeignKey = models.ForeignKey(
        to='mortgage.MortgageProgram',
        on_delete=models.CASCADE,
        related_name='mortgage_program_condition_through',
    )

    class Meta:
        managed = False
        db_table = 'mortgage_calculator_condition_program_through'


class MortgageConditionBankThrough(models.Model):
    """
    Отношения ип калькулят условий к банкам.
    """
    mortgage_condition: models.ForeignKey = models.ForeignKey(
        to="mortgage.MortgageCalculatorCondition",
        on_delete=models.CASCADE,
        related_name='mortgage_condition_bank_through',
    )
    mortgage_bank: models.ForeignKey = models.ForeignKey(
        to='mortgage.MortgageBank',
        on_delete=models.CASCADE,
        related_name='mortgage_bank_condition_through',
    )

    class Meta:
        managed = False
        db_table = 'mortgage_calculator_condition_bank_through'
