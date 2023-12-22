from tortoise import Model, fields

from common.orm.entities import BaseRepo
from common.orm.mixins import CRUDMixin


class MortgageApplicationStatus(Model):
    """
    12.6 Статусы заявки на ипотеку через застройщика.
    """
    id: int = fields.IntField(description="ID", pk=True)
    name: str = fields.CharField(max_length=255, description="Название статуса")
    priority: int = fields.IntField(default=0, description="Приоритет")
    amocrm_statuses: fields.ManyToManyRelation["AmocrmStatus"] = fields.ManyToManyField(
        model_name="models.AmocrmStatus",
        related_name="mortgage_application_statuses",
        through="mortgage_application_status_amocrm_statuses_through",
        description="Статусы сделки",
        null=True,
        on_delete=fields.CASCADE,
        backward_key="mortgage_application_status_id",
        forward_key="amocrm_status_id",
    )

    mortgage_dev_ticket: fields.ForeignKeyRelation["MortgageDeveloperTicket"]

    def __str__(self) -> str:
        return self.name

    class Meta:
        table = "mortgage_application_status"


class MortgageApplicationStatusAmocrmStatusesThrough(Model):
    """
    Промежуточная таблица статусов заявки на ипотеку через застройщика к статусам сделок.
    """

    id: int = fields.IntField(description="ID", pk=True)
    mortgage_application_status: fields.ForeignKeyRelation[MortgageApplicationStatus] = fields.ForeignKeyField(
        model_name="models.MortgageApplicationStatus",
        related_name="mortgage_application_status_amocrm_statuses_through",
        on_delete=fields.CASCADE,
    )
    amocrm_status: fields.ForeignKeyRelation["AmocrmStatus"] = fields.ForeignKeyField(
        model_name="models.AmocrmStatus",
        related_name="mortgage_application_status_amocrm_statuses_through",
        on_delete=fields.CASCADE,
    )

    class Meta:
        table = "mortgage_application_status_amocrm_statuses_through"


class MortgageApplicationStatusRepo(BaseRepo, CRUDMixin):
    """
    Репо статусов заявки ик от застройщика.
    """
    model = MortgageApplicationStatus
