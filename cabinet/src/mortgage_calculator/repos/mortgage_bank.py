from typing import Optional, Any

from tortoise import Model, fields

from common import cfields
from common.orm.entities import BaseRepo
from common.orm.mixins import CRUDMixin


class MortgageBank(Model):
    """
    Банки под ипотечный калькулятор.
    """
    id: int = fields.IntField(description="ID", pk=True)
    bank_name: str = fields.TextField(description="Имя банка")
    bank_icon: Optional[dict[str, Any]] = cfields.MediaField(
        description="Иконка банка", max_length=300, null=True
    )
    priority: int = fields.IntField(default=0, description="Приоритет")
    external_code: str = fields.TextField(description="Внешний код")
    uid: str = fields.CharField(max_length=255, description="UID")

    def __str__(self) -> str:
        return self.bank_name

    class Meta:
        table = "mortgage_calculator_banks"


class MortgageBanksRepo(BaseRepo, CRUDMixin):
    """
    Репозиторий банков и/к .
    """
    model = MortgageBank
