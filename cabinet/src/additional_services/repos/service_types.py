from tortoise import fields

from common.orm.mixins import ReadWriteMixin
from ..entities import BaseAdditionalServiceDatabaseModel, BaseAdditionalServiceRepo


class AdditionalServiceType(BaseAdditionalServiceDatabaseModel):
    """
    Тип категорий (видов) услуг
    """

    id: int = fields.IntField(description="ID", pk=True)
    title: str = fields.CharField(description="Название", max_length=150)
    services: fields.ReverseRelation["AdditionalService"]

    class Meta:
        table = "additional_services_service_type"


class AdditionalServiceTypeRepo(BaseAdditionalServiceRepo, ReadWriteMixin):
    """
    Репозиторий типа категорий услуг
    """

    model = AdditionalServiceType
