from datetime import datetime
from typing import Optional

from tortoise import Model, fields

from common import cfields
from common.orm.entities import BaseRepo
from common.orm.mixins import CRUDMixin
from src.mortgage_calculator.constants import MortgageApprove


class MortgageConditionMatrix(Model):
    """
    Матрица условий.
    """

    id: int = fields.IntField(description="ID", pk=True)

    name: str = fields.CharField(description="Название", max_length=100)

    amocrm_statuses: fields.ManyToManyRelation["AmocrmStatus"] = fields.ManyToManyField(
        model_name="models.AmocrmStatus",
        related_name="mortgagematrix_amocrm_statuses",
        through="mortgage_calсutator_matrix_amocrm_statuses_through",
        description="Статусы сделки",
        null=True,
        on_delete=fields.CASCADE,
        backward_key="mortgage_matrix_condition_id",
        forward_key="amocrm_status_id",
    )

    is_there_agent: Optional[bool] = fields.BooleanField(description="Можно ли подать заявку на ипотеку, если есть агент", default=False)

    default_value: Optional[bool] = fields.BooleanField(description="По умолчанию", default=False)

    # Пока оставить до выяснения что делать с колонкой
    # is_apply_for_mortgage: str = cfields.CharChoiceField( 
    #     description="Можно ли подать заявку на ипотеку",
    #     max_length=50,
    #     default=MortgageApprove.NO,
    #     choice_class=MortgageApprove,
    # )

    created_at: datetime = fields.DatetimeField(
        description="Дата и время создания", auto_now_add=True
    )

    updated_at: datetime = fields.DatetimeField(
        description="Дата и время обновления", auto_now=True
    )

    def __str__(self) -> str:
        return self.name

    class Meta:
        table = "mortgage_calculator_condition_matrix"


class MortgageMatrixConditionAmocrmStatusesThrough(Model):
    """
    Промежуточная таблица матрицы условий к статусам сделок.
    """

    id: int = fields.IntField(description="ID", pk=True)
    mortgage_matrix_condition: fields.ForeignKeyRelation[MortgageConditionMatrix] = fields.ForeignKeyField(
        model_name="models.MortgageConditionMatrix",
        related_name="mortgage_matrix_condition_amocrm_statuses_through",
        description="Условия",
        on_delete=fields.CASCADE,
        backward_key="mortgage_matrix_condition_id",
    )
    amocrm_status: fields.ForeignKeyRelation["AmocrmStatus"] = fields.ForeignKeyField(
        model_name="models.AmocrmStatus",
        related_name="amocrm_status_matrix_condition_through",
        description="Статусы сделок",
        on_delete=fields.CASCADE,
        backward_key="amocrm_status_id",
    )

    class Meta:
        table = "mortgage_calсutator_matrix_amocrm_statuses_through"


class MortgageConditionMatrixRepo(BaseRepo, CRUDMixin):
    """
    Репозиторий матрицы условий и/к.
    """

    model = MortgageConditionMatrix
