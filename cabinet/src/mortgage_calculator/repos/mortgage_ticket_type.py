from tortoise import Model, fields

from common.orm.entities import BaseRepo
from common.orm.mixins import CRUDMixin


class MortgageTicketType(Model):
    """
    Тип заявки на ипотеку
    """

    id: int = fields.IntField(pk=True, description="ID")
    title = fields.CharField(max_length=100, null=True, description="Название")
    amocrm_id: int | None = fields.BigIntField(
        description="ID в AmoCRM", null=True, unique=True
    )

    class Meta:
        table = "mortgage_ticket_types"


class MortgageTicketTypeRepo(BaseRepo, CRUDMixin):
    """
    Репозиторий типа заявок на ипотеку
    """

    model = MortgageTicketType
