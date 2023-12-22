from typing import Optional, Any

from tortoise import Model, fields

from common import cfields
from common.orm.entities import BaseRepo
from common.orm.mixins import CRUDMixin


class MortgageBank(Model):
    """
    12.10 Банки под ипотечный калькулятор.
    """
    id: int = fields.IntField(description="ID", pk=True)
    name: str = fields.CharField(max_length=255, description="Имя банка")
    icon: Optional[dict[str, Any]] = cfields.MediaField(
        description="Иконка банка", max_length=300, null=True
    )
    priority: int = fields.IntField(default=0, description="Приоритет")
    external_code: str = fields.TextField(description="Внешний код")
    uid: str = fields.CharField(max_length=255, description="UID")

    mortgage_conditions: fields.ManyToManyRelation["MortgageBank"]

    def __str__(self) -> str:
        return self.name

    class Meta:
        table = "mortgage_calculator_banks"


class MortgageBankRepo(BaseRepo, CRUDMixin):
    """
    Репозиторий банков и/к .
    """
    model = MortgageBank
