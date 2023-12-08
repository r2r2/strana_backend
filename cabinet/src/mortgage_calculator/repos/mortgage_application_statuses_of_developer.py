from tortoise import Model, fields

from common.orm.entities import BaseRepo
from common.orm.mixins import CRUDMixin


class MortgageApplicationStatus(Model):
    """
    Статусы заявки ик от застройщика.
    """
    id: int = fields.IntField(description="ID", pk=True)
    status_name: str = fields.TextField(description="Названеи статуса")
    priority: int = fields.IntField(default=0, description="Приоритет")
    external_code: str = fields.TextField(description="Внешний код")

    def __str__(self) -> str:
        return self.status_name

    class Meta:
        table = "mortgage_application_status"


class MortgageApplicationStatusRepo(BaseRepo, CRUDMixin):
    """
    Репо статусов заявки ик от застройщика.
    """
    model = MortgageApplicationStatus
