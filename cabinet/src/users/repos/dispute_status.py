from tortoise import Model, fields

from common.orm.mixins import ReadWriteMixin
from src.users.entities import BaseUserRepo


class DisputeStatus(Model):
    """
    Таблица статусов оспаривания
    """

    id: int = fields.IntField(description="ID", pk=True)
    title: str = fields.CharField(description="Название", max_length=255)
    checks: fields.ReverseRelation["Check"]

    class Meta:
        table = "users_dispute_statuses"


class DisputeStatusRepo(BaseUserRepo, ReadWriteMixin):
    """
    Репозиторий статусов оспаривания
    """

    model: DisputeStatus = DisputeStatus
