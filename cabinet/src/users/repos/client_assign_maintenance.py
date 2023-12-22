from datetime import datetime

from tortoise import Model, fields

from common.orm.mixins import CRUDMixin, CountMixin
from src.users.entities import BaseUserRepo


class ClientAssignMaintenance(Model):
    """
    Модель подтверждения закрепления клиента за агентом
    """
    id: int = fields.IntField(pk=True, description="ID")
    client_phone: str = fields.CharField(description="Номер телефона", max_length=20)
    successful_assign: bool = fields.BooleanField(description="Успешная проверка")
    broker_amocrm_id: int = fields.BigIntField(description="ID в AmoCRM")
    created_at: datetime = fields.DatetimeField(description="Дата и время создания", auto_now_add=True)

    def __str__(self):
        return f"{self.client_phone}"

    class Meta:
        table = "users_client_assign_maintenance"


class ClientAssignMaintenanceRepo(BaseUserRepo, CRUDMixin, CountMixin):
    """
    Репозиторий для работы с моделью ConfirmClientAssign
    """
    model = ClientAssignMaintenance
