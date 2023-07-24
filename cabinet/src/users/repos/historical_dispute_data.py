from datetime import datetime
from typing import Optional

from tortoise import Model, fields
from tortoise.fields import ForeignKeyNullableRelation

from common.orm.mixins import CRUDMixin
from src.agencies.repos import Agency
from src.users.entities import BaseUserRepo
from src.users.repos import User, UniqueStatus


class HistoricalDisputeData(Model):
    """
    Учет исторических данных оспаривания
    """
    id: int = fields.IntField(pk=True)
    dispute_agent: ForeignKeyNullableRelation[User] = fields.ForeignKeyField(
        description="Оспаривающий агент",
        model_name="models.User",
        on_delete=fields.SET_NULL,
        related_name="historical_dispute_data_dispute_agent",
        null=True,
    )
    dispute_agent_agency: ForeignKeyNullableRelation[Agency] = fields.ForeignKeyField(
        description="Агентство",
        model_name="models.Agency",
        on_delete=fields.SET_NULL,
        related_name="historical_dispute_data_agent_agency",
        null=True,
    )
    client: ForeignKeyNullableRelation[User] = fields.ForeignKeyField(
        description="Клиент",
        model_name="models.User",
        on_delete=fields.SET_NULL,
        related_name="historical_dispute_data_client",
        null=True,
    )
    client_agency: ForeignKeyNullableRelation[Agency] = fields.ForeignKeyField(
        description="Агентство",
        model_name="models.Agency",
        on_delete=fields.SET_NULL,
        related_name="historical_dispute_data_client_agency",
        null=True,
    )
    agent: ForeignKeyNullableRelation[User] = fields.ForeignKeyField(
        description="Агент",
        model_name="models.User",
        on_delete=fields.SET_NULL,
        related_name="historical_dispute_data_agent",
        null=True,
    )
    dispute_requested: Optional[datetime] = fields.DatetimeField(
        description="Время оспаривания",
        null=True,
    )
    admin: ForeignKeyNullableRelation[User] = fields.ForeignKeyField(
        description="Админ",
        model_name="models.User",
        on_delete=fields.SET_NULL,
        related_name="historical_dispute_data_admin",
        null=True,
    )
    admin_update: Optional[datetime] = fields.DatetimeField(
        description="Время обновления админом",
        null=True,
    )
    admin_unique_status: fields.ForeignKeyNullableRelation[UniqueStatus] = fields.ForeignKeyField(
        description="Статус уникальности",
        model_name="models.UniqueStatus",
        on_delete=fields.CASCADE,
        related_name="historical_dispute_data_admin_unique_status",
        null=True,
    )

    class Meta:
        table = "historical_dispute_data"
        table_description = "Учет исторических данных оспаривания"


class HistoricalDisputeDataRepo(BaseUserRepo, CRUDMixin):
    """
    Репозиторий учета исторических данных оспаривания
    """
    model = HistoricalDisputeData
