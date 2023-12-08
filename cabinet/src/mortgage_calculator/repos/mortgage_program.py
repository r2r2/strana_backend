from tortoise import Model, fields

from common.orm.entities import BaseRepo
from common.orm.mixins import CRUDMixin


class MortgageProgram(Model):
    """
    Программы под ипотечный калькулятор.
    """
    id: int = fields.IntField(description="ID", pk=True)
    program_name: str = fields.TextField(description="Имя банка")
    priority: int = fields.IntField(default=0, description="Приоритет")
    external_code: str = fields.TextField(description="Внешний код")
    slug: str = fields.CharField(max_length=255, description="Слаг")

    def __str__(self) -> str:
        return self.program_name

    class Meta:
        table = "mortgage_calculator_program"


class MortgageProgramRepo(BaseRepo, CRUDMixin):
    """
    Репозиторий ипотечных программ и/к .
    """
    model = MortgageProgram
