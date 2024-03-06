from datetime import date, datetime

from tortoise import Model, fields

from common import cfields
from common.orm.mixins import CRUDMixin
from src.mortgage.entities import BaseMortgageRepo


class DduContract(Model):
    """
    Договор ДДУ.
    """
    id: int = fields.IntField(description="ID", pk=True)
    number: str = fields.CharField(
        max_length=100,
        description="Номер договора",
    )
    contract_date: date = fields.DateField(
        description="Дата заключения",
    )
    reference_file: str = cfields.MediaField(
        description="Файл для ознакомления",
        max_length=2000,
        null=True,
    )
    created_at: datetime = fields.DateField(
        description="Дата создания",
        auto_now_add=True,
    )
    updated_at: datetime = fields.DateField(
        description="Дата обновления",
        auto_now=True,
    )
    status: str = fields.CharField(
        max_length=100,
        description="Статус договора",
    )

    def __str__(self) -> str:
        return f"ДДУ. {self.number}"

    class Meta:
        table = "ddu_contract"


class DduContractRepo(BaseMortgageRepo, CRUDMixin):
    """
    Репозиторий договоров ДДУ.
    """
    model = DduContract
