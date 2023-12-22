from tortoise import Model, fields

from common.orm.entities import BaseRepo
from common.orm.mixins import CRUDMixin


class MortgageProgram(Model):
    """
    Ипотечные программы
    """
    id: int = fields.IntField(description="ID", pk=True)
    name: str = fields.CharField(max_length=255, description="Название программы")
    priority: int = fields.IntField(default=0, description="Приоритет")
    external_code: str = fields.TextField(description="Внешний код")
    slug: str = fields.CharField(max_length=255, description="Слаг")

    mortgage_conditions: fields.ManyToManyRelation["MortgageCalculatorCondition"]

    def __str__(self) -> str:
        return self.name

    class Meta:
        table = "mortgage_calculator_program"


class MortgageProgramRepo(BaseRepo, CRUDMixin):
    """
    Репозиторий ипотечных программ и/к .
    """
    model = MortgageProgram
