from tortoise import fields

from common.orm.mixins import ReadWriteMixin
from ..entities import BaseAdditionalServiceDatabaseModel, BaseAdditionalServiceRepo


class AdditionalServiceCondition(BaseAdditionalServiceDatabaseModel):
    """
    Модель "Как получить услугу"
    """

    id: int = fields.IntField(description="ID", pk=True)
    title: str = fields.CharField(description="Название", max_length=150)
    steps: fields.ReverseRelation["AdditionalServiceConditionStep"]

    class Meta:
        table = "additional_services_condition"


class AdditionalServiceConditionRepo(BaseAdditionalServiceRepo, ReadWriteMixin):
    """
    Репозиторий "Как получить услугу"
    """

    model = AdditionalServiceCondition
