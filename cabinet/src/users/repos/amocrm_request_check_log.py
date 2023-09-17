from tortoise import Model, fields
from tortoise.fields import ForeignKeyNullableRelation

from common import orm
from common.orm.mixins import GenericMixin
from .history_check import CheckHistory
from ..entities import BaseUserRepo


class AmoCrmCheckLog(Model):
    """
    Лог запросов истории проверки в AmoCrm
    """

    id: int = fields.BigIntField(description="ID", pk=True)
    check_history: ForeignKeyNullableRelation[CheckHistory] = fields.ForeignKeyField(
        description="Проверка уникальности",
        model_name="models.CheckHistory",
        on_delete=fields.SET_NULL,
        related_name="history_check_log",
        null=True,
    )
    route: str = fields.CharField(description="Статус ответа", max_length=50)
    status: int = fields.IntField(description="Статус ответа")
    query: str = fields.CharField(description="Квери запроса", max_length=100)
    data: str = fields.TextField(description="Тело ответа(Пустое если статус ответа 200)", null=True)

    class Meta:
        table = "users_amocrm_checks_history_log"


class AmoCrmCheckLogRepo(BaseUserRepo, GenericMixin):
    """
    Репозиторий логов запросов истории проверки в AmoCrm
    """
    model = AmoCrmCheckLog
    q_builder: orm.QBuilder = orm.QBuilder(AmoCrmCheckLog)
