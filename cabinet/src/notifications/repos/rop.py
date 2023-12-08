from tortoise import Model, fields

from ..entities import BaseNotificationRepo
from common.orm.mixins import ReadOnlyMixin


class RopEmailsDispute(Model):
    """
    Таблица с почтами Руководителей отдела продаж, не путать с юзерами типа роп
    """

    id: int = fields.IntField(description="ID", pk=True, index=True)
    fio: str = fields.CharField(description="ФИО ропа", max_length=100)
    project: fields.ForeignKeyRelation = fields.ForeignKeyField(
        description="Проект",
        model_name="models.Project",
        related_name="project_rop",
        on_delete=fields.CASCADE,
    )
    email: str = fields.CharField(
        description="Email", max_length=100
    )

    class Meta:
        table = "notifications_rop_emails_dispute"


class RopEmailsDisputeRepo(BaseNotificationRepo, ReadOnlyMixin):
    """
    Репозиторий таблицы с почтами Руководителей отдела продаж, не путать с юзерами типа роп
    """
    model = RopEmailsDispute
