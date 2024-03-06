from tortoise import Model, fields
from tortoise.fields import ForeignKeyNullableRelation

from common.orm.mixins import CreateMixin, ListMixin
from common.loggers.repos import AbstractLogMixin
from ..repos import Agency
from ..entities import BaseAgencyRepo


class AgencyLog(Model, AbstractLogMixin):
    """
    Лог агентства
    """

    agency: ForeignKeyNullableRelation[Agency] = fields.ForeignKeyField(
        description="Агентство",
        model_name="models.Agency",
        related_name="agency_logs",
        on_delete=fields.SET_NULL,
        null=True,
    )

    class Meta:
        table = "agencies_agencylog"


class AgencyLogRepo(BaseAgencyRepo, CreateMixin, ListMixin):
    """
    Репозиторий лога агентства
    """

    model = AgencyLog
