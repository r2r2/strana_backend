from tortoise import fields

from common.orm.mixins import ReadWriteMixin
from ..entities import BaseAdditionalServiceDatabaseModel, BaseAdditionalServiceRepo


class AdditionalServiceGroupStatus(BaseAdditionalServiceDatabaseModel):
    """
    Модель группирующих статусов для доп услуг
    """

    id: int = fields.IntField(description="ID", pk=True)
    name: str = fields.CharField(max_length=150, description="Название", null=True)
    slug: str = fields.CharField(
        max_length=50, description="slug", null=True, unique=True
    )
    sort: int = fields.IntField(description="Приоритет", default=0)

    def __str__(self):
        return self.name

    class Meta:
        table = "additional_services_group_statuses"


class AdditionalServiceGroupStatusRepo(BaseAdditionalServiceRepo, ReadWriteMixin):
    """
    Репозиторий группирующих статусов для доп услуг
    """

    model = AdditionalServiceGroupStatus
